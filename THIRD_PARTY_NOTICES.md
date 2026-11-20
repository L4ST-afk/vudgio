# 第三方许可全文

本项目并入或改写了下列来源的判据形态，其许可全文如下（原样保留）。逐条「用了什么、边界在哪」见 `references/sources.md`。

## emil-design-eng（动效）

Upstream: https://github.com/emilkowalski/skills
Used for: 动画四问、三条缓动曲线、时长表、组件手感、性能红线、Before/After/Why 写法。只取判据形态并改写，未转载实现代码。

```
MIT License

Copyright (c) 2026 Emil Kowalski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Lens 材质语义与交互反馈判据

Upstream: https://github.com/ruiqichenbiec/design-systems（MIT 项目）
Used for: `references/apple-design...` 对应卷 §12A 引用的七类材质语义与反馈判据；只取判据，不引入实现。

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Alpine.js 3.17.4

Bundled at `assets/vendor/alpine.min.js`.
Upstream: https://github.com/alpinejs/alpine — MIT License.

```
MIT License

Copyright (c) 2021 Caleb Porzio and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Instrument Serif

Bundled at `assets/fonts/instrument-serif/InstrumentSerif-Regular.ttf`.
Upstream: https://github.com/Instrument/instrument-serif — SIL Open Font License 1.1.
Full license text is retained in `assets/fonts/instrument-serif/OFL.txt` (bundled); do not remove it.

## impeccable（架构）

Upstream: https://github.com/（本机库内技能 impeccable）
License: Apache License, Version 2.0
Used for: 四型（说服／操作／阅读／体验）、命令面、craft-floor 质量地板、Subtract before add、PRODUCT/DESIGN 双产物。只取判据形态，不搬 launcher／detector hook／live 机制。

本项目**不转载**其源码；Apache-2.0 许可全文见：
https://www.apache.org/licenses/LICENSE-2.0

## 其余来源

refactoring-ui、apple-design、design-taste-frontend、web-design-engineer 及若干本机私有工作法档，本项目只取判据形态并在 `references/sources.md` 逐条登记出处与边界，不转载正文，故无第三方许可全文需附。若其中任一来源要求署名，以 `references/sources.md` 该条为准。

## 自建兜底主题（非第三方资产）

`assets/themes/friendship-bldg.css` 是本项目独立维护的自建主题，不属于第三方资产，故无外部许可全文需附。其配色意象来自上海展览中心（原中苏友好大厦），由本机自建皮肤改造并删去 deck/demo 专属规则；头部注释自述来源与「非默认、仅兜底」约束。改造前后源文件 sha256 未变（只读复制）。
