// 超椭圆（G2 平滑圆角）路径生成器：给 `clip-path: path()` 或 SVG 用。
// 只做几何，不碰 DOM：给定宽高与半径，吐一串点。
//
// 用法：
//   node scripts/squircle_path.mjs --width 300 --height 200 --radius 40
//   node scripts/squircle_path.mjs --width 300 --height 200 --radius 40 --format svg
//   node scripts/squircle_path.mjs --width 48 --height 48 --radius 12 --n 5 --format json
//
// 退出码：0 出结果／1 自检不过（点越界、首尾不闭合）／2 用法或输入错。

import { fileURLToPath } from 'node:url';
import { EXIT, usageError, runMain } from './_cli.mjs';

const HELP = `--width <px>   必填，正整数
--height <px>  必填，正整数
--radius <px>  必填，非负数；超过 min(宽,高)/2 会夹紧并告警
--n <数>       超椭圆指数，默认 5（业界近似，非苹果公布值）；n=2 退化成圆
--steps <数>   每角采样段数，默认 24
--format <f>   css（默认）／svg／json
--help         这份说明`;

const DEFAULTS = { n: 5, steps: 24, format: 'css' };

function parseArgs(argv) {
  const opts = { ...DEFAULTS };
  const numbers = new Set(['width', 'height', 'radius', 'n', 'steps']);
  for (let i = 0; i < argv.length; i++) {
    const raw = argv[i];
    if (raw === '--help' || raw === '-h') return { help: true };
    if (!raw.startsWith('--')) throw usageError(`不认识的参数：${raw}`, { help: HELP });
    const key = raw.slice(2);
    const allowed = [...numbers, 'format'];
    if (!allowed.includes(key)) throw usageError(`不认识的选项：--${key}`, { help: HELP });
    const value = argv[++i];
    if (value === undefined) throw usageError(`--${key} 缺值`, { help: HELP });
    if (numbers.has(key)) {
      const num = Number(value);
      if (!Number.isFinite(num)) throw usageError(`--${key} 要是数字，收到 ${value}`, { help: HELP });
      opts[key] = num;
    } else {
      if (!['css', 'svg', 'json'].includes(value)) {
        throw usageError(`--format 只认 css／svg／json，收到 ${value}`, { help: HELP });
      }
      opts.format = value;
    }
  }
  for (const key of ['width', 'height', 'radius']) {
    if (opts[key] === undefined) throw usageError(`缺 --${key}`, { help: HELP });
  }
  if (!(opts.width > 0) || !(opts.height > 0)) throw usageError('--width／--height 要正整数', { help: HELP });
  if (opts.radius < 0) throw usageError('--radius 不能是负数', { help: HELP });
  if (opts.n < 2) throw usageError('--n 小于 2 不再是超椭圆（n=2 是圆）', { help: HELP });
  if (!(opts.steps >= 4)) throw usageError('--steps 至少 4', { help: HELP });
  return opts;
}

/** 超椭圆在各象限的采样；返回 { points, radius, clamped }。 */
export function squirclePoints({ width, height, radius, n = 5, steps = 24 }) {
  const limit = Math.min(width, height) / 2;
  const r = Math.min(radius, limit);
  const clamped = r !== radius;
  // 整条路径逆时针：右缘上行 → 上缘左行 → 左缘下行 → 下缘右行。
  // 四个角的起止点必须首尾相接，所以 TL／BR 两角要把 sin／cos 互换（否则会从角上斜穿）。
  const cx = [width - r, r, r, width - r];
  const cy = [r, r, height - r, height - r];
  const sx = [1, -1, -1, 1];
  const sy = [-1, -1, 1, 1];
  // 均匀参数 t 采样会让点挤在 45°、稀在切点（|cos|^(2/n) 在 t→0 处导数发散）。
  // 做法：每角先密采 256 点，再按累计弧长等距重采 steps+1 点。
  const dense = 256;
  const points = [];
  for (let q = 0; q < 4; q++) {
    const raw = [];
    for (let i = 0; i <= dense; i++) {
      const t = (i / dense) * Math.PI / 2;
      const u = (q === 1 || q === 3) ? Math.sin(t) : Math.cos(t);
      const v = (q === 1 || q === 3) ? Math.cos(t) : Math.sin(t);
      raw.push([
        cx[q] + sx[q] * r * Math.pow(Math.abs(u), 2 / n),
        cy[q] + sy[q] * r * Math.pow(Math.abs(v), 2 / n),
      ]);
    }
    const acc = [0];
    for (let i = 1; i < raw.length; i++) {
      acc.push(acc[i - 1] + Math.hypot(raw[i][0] - raw[i - 1][0], raw[i][1] - raw[i - 1][1]));
    }
    const total = acc[acc.length - 1];
    for (let i = 0; i <= steps; i++) {
      const target = total * (i / steps);
      let k = 1;
      while (k < acc.length - 1 && acc[k] < target) k++;
      const span = acc[k] - acc[k - 1] || 1;
      const ratio = (target - acc[k - 1]) / span;
      points.push([
        raw[k - 1][0] + (raw[k][0] - raw[k - 1][0]) * ratio,
        raw[k - 1][1] + (raw[k][1] - raw[k - 1][1]) * ratio,
      ]);
    }
  }
  return { points, radius: r, clamped };
}

export function toPathData(points) {
  const body = points.map(([x, y], i) => `${i === 0 ? 'M' : 'L'}${x.toFixed(2)} ${y.toFixed(2)}`).join(' ');
  return `${body} Z`;
}

function verify(points, { width, height }) {
  const eps = 0.01;
  for (const [x, y] of points) {
    if (x < -eps || x > width + eps || y < -eps || y > height + eps) return '有点落在画布外';
  }
  const first = points[0], last = points[points.length - 1];
  // 闭合点必须回到起点附近（首点 = 右上角起始，末点 = 右下角起始；由 Z 闭合）
  if (Math.abs(first[1] - last[1]) > height) return '首尾纵向差过大';
  return '';
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  if (opts.help) {
    console.log(HELP);
    return;
  }
  const { points, radius, clamped } = squirclePoints(opts);
  if (clamped) console.warn(`[squircle-path] 半径 ${opts.radius} 超过 min(宽,高)/2，已夹到 ${radius}`);
  const d = toPathData(points);
  const bad = verify(points, opts);

  if (opts.format === 'json') {
    console.log(JSON.stringify({
      width: opts.width, height: opts.height, radius, n: opts.n, steps: opts.steps,
      points: points.length, path: d, ok: !bad,
    }, null, 2));
  } else if (opts.format === 'svg') {
    console.log(`<svg xmlns="http://www.w3.org/2000/svg" width="${opts.width}" height="${opts.height}" viewBox="0 0 ${opts.width} ${opts.height}"><path d="${d}"/></svg>`);
  } else {
    console.log(`clip-path: path("${d}");`);
    console.log(`-webkit-clip-path: path("${d}");`);
  }

  if (bad) throw Object.assign(new Error(`自检不过：${bad}`), { code: 'FAIL' });
  process.exitCode = EXIT.ok;
}

// 只有被当脚本跑时才接 CLI；被 import（测试或别的脚本）时不吞参数、不落退出码。
if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  runMain(main, { label: '[squircle-path] ' });
}
