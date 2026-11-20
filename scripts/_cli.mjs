// 三件 mjs 共用的小层：退出码与用法错。只放这三样，不装参数解析——
// 各件的选项面差别太大，合成一个解析器只会把三套口径搅成一套。
//
// 用法：import { EXIT, usageError, runMain } from './_cli.mjs';

/** 退出码契约：0 跑通／1 有检查项不过或运行期失败／2 用法或输入错。 */
export const EXIT = Object.freeze({ ok: 0, fail: 1, usage: 2 });

/**
 * 造一条「用法或输入错」。调用方只负责 throw，落码由 runMain 统一映射，
 * 免得每处 catch 各写一遍三元。
 */
export function usageError(message, { example, help } = {}) {
  const lines = [message];
  if (example) lines.push(`示例：${example}`);
  if (help) lines.push(`全部选项：${help}`);
  const error = new Error(lines.join('\n'));
  error.code = 'USAGE';
  return error;
}

/**
 * 跑主函数并把异常落成退出码。返回的 Promise 结束即已设好 process.exitCode。
 * label 是错误前缀（各件不同，如 `[curate-media] `、`prep-image：`），已含分隔符。
 */
export async function runMain(main, { label = '' } = {}) {
  try {
    await main();
  } catch (error) {
    console.error(`${label}${error.message}`);
    process.exitCode = error.code === 'USAGE' ? EXIT.usage : EXIT.fail;
  }
}
