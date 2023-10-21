---
title: "[译] 一文了解 WebAssembly 及其发展历史件"
date: 2023-08-18
comments: true
description: 在这篇文章中，你会了解到什么是汇编语言，为什么汇编语言在 Web 平台中非常有用，然后了解 WebAssembly 是如何在 asm.js 这个临时解决方案的基础上产生发展的。
---

> 原文链接: https://web.dev/what-is-webassembly/
>
> 原文作者：[Thomas Steiner](https://web.dev/authors/thomassteiner/)

自从网络不仅成为文档平台，也成为应用程序平台以来，那些最先进的 Web 应用已经将浏览器推向了极限。在许多高级语言中，我们都能看到通过低级语言接口来让程序更“贴近硬件”的方法，例如 Java 的 [Java Native Interface](https://web.archive.org/web/20080330002620/http://today.java.net/pub/a/today/2006/10/19/invoking-assembly-language-from-java.html)。对于 JavaScript 来说，这个低级语言就是 WebAssembly。在这篇文章中，你会了解到什么是汇编语言，为什么汇编语言在 Web 平台中非常有用，然后了解 WebAssembly 是如何在 asm.js 这个临时解决方案的基础上产生发展的。

## 汇编语言

你用汇编语言写过程序吗？在计算机编程中，汇编语言——通常被简称为 Assembly 或者缩写为 ASM——指代所有低级语言，这类语言的语句和体系架构的机器码有着很强的对应关系。

以 [英特尔 64 与 IA-32 架构为例](https://software.intel.com/en-us/download/intel-64-and-ia-32-architectures-sdm-combined-volumes-1-2a-2b-2c-2d-3a-3b-3c-3d-and-4) (PDF) 为例，其 [`MUL`](https://www.felixcloutier.com/x86/mul) 指令（也就是乘法 multiplication）会对第一个操作数（目标操作数）和第二个操作数（源操作数）进行无符号惩罚，然后将结果存储在目标操作数中。简单来说，目标操作数是一个位于寄存器 `AX` 中的隐含操作数，而源操作数则位于类似 `CX` 这样的通用寄存器中。最后结果会被存储到 `AX` 寄存器中。下面是一个 x86 代码的例子：

```assembly
mov ax, 5  ; 设置 AX 寄存器的值为 5
mov cx, 10 ; 设置 CX 寄存器的值为 10
mul cx     ; 将 AX 和 CX 中的值✖️，并把结果存储到 AX 寄存器中
```

比较一下，如果让你用 JavaScript 代码来实现 5 \* 10 这个功能，大概会是这样的：

```js
const factor1 = 5;
const factor2 = 10;
const result = factor1 * factor2;
```

相比于使用高级且可读性强的语言，使用汇编语言来实现的好处是它足够低级和接近硬件，因此执行效率非常高。在上面的例子中两者的效率区别不会很明显，但对于更复杂的操作来说，就会有很大的不同了。

从名字就可以看出来，x86 代码依赖于 x86 架构。是否有一种方法让我们可以编写不依赖于特定架构的汇编语言，同时又仍然保留汇编语言的性能优势？

## asm.js

编写不依赖于特定架构的汇编语言的第一步尝试是 [asm.js](http://asmjs.org/spec/latest/)，它是一个 JavaScript 的严格子集，可作为编译器的低级且高效的目标语言。这个子语言有效地提供了一个供 C 或 C++ 等内存不安全语言使用的沙盒虚拟机。结合静态和动态的验证，JavaScript 可以采用 AOT（ahead-of-time）优化编译策略来编译出有效的 asm.js 代码。使用具有手动内存管理功能的静态类型语言（如 C）编写的代码由“源码到源码”编译器（如早期的 Emscripten，基于 LLVM）进行翻译。

通过将语言功能限制在适合 AOT 的范围内，程序运行的性能得到了提高。火狐 22 是第一个支持 asm.js 的浏览器，以 OdinMonkey 的名称发布。Chrome 在第 61 版中增加了对 asm.js 的支持。虽然 asm.js 仍能在浏览器中运行，但它已被 WebAssembly 所取代。目前使用 asm.js 的原因是，它可以作为不支持 WebAssembly 的浏览器的替代方案。

## WebAssembly

WebAssembly 是一种低级汇编语言，采用紧凑的二进制格式，其运行性能接近原生语言。它可以作为 C/C++ 和 Rust 等语言的编译目标，使其能在网络上运行。对 Java、Kotlin 和 Dart 等自动内存管理语言的支持正在进行中，不久就会推出。WebAssembly 的设计目的是与 JavaScript 同时运行，使两者能够协同工作。

WebAssembly 程序还可以在浏览器外的环境中运行，这要归功于 [WASI](https://wasi.dev/)（WebAssembly 系统接口），它是 WebAssembly 的模块化系统接口。WASI 可以跨操作系统移植，目的是保证安全，并能在沙箱环境中运行。

WebAssembly 代码（二进制代码，即字节码）能够在跨平台虚拟机（VM）上运行。与 JavaScript 相比，WebAssembly 字节码的解析和执行速度更快，代码表示也更紧凑。

从概念上讲，指令的执行是通过传统的程序计数器（program counter）机制进行的，计数器随着指令的运行递增。在实践中，大多数 Wasm 引擎会将 Wasm 字节码编译为机器码，然后执行机器码。指令可分为两类：

- **控制指令**形成控制结构，它会从堆栈中弹出参数值，可能会更改程序计数器，并将结果值推入堆栈。
- **简单指令**从堆栈中弹出参数值，将运算符应用于参数值，然后将结果值推入堆栈，随后程序计数器隐式递增。

回到之前的例子，下面的 WebAssembly 代码相当于刚刚的 x86 代码：

```assembly
i32.const 5  ; 将整数值 5 推入栈内
i32.const 10 ; 将整数值 10 推入栈内
i32.mul      ; 将栈内最新的两个数推出，把它们相乘，然后把结果推到栈中
```

asm.js 仅靠软件就能实现，也就是说其代码可以在任何 JavaScript 引擎中运行（即使未经优化），而 WebAssembly 需要所有浏览器供应商一致同意的新功能才能运行。WebAssembly 于 2015 年公布，2017 年 3 月首次发布，2019 年 12 月 5 日成为 [W3C 推荐标准](https://www.w3.org/TR/wasm-core-1/)。W3C 维护着 WebAssembly 标准，所有主要浏览器供应商和其他相关方都参与了标准的贡献。从 2017 年以来，WebAssembly 的浏览器支持实现了普及。

![image-20230818213522769](/Users/wuzikang/Projects/wzk-blog/content/post/webassembly/image-20230818213522769.png)

WebAssembly 代码有两种格式：[文本格式](https://developer.mozilla.org/docs/WebAssembly/Understanding_the_text_format) 和 [二进制格式](https://developer.mozilla.org/docs/WebAssembly/Text_format_to_wasm)。你刚刚看到的代码是文本格式的。

### 文本表示法

WebAssembly 的文本格式基于 [S-expressions](https://developer.mozilla.org/docs/WebAssembly/Understanding_the_text_format#s-expressions)，通常使用 `.wat` 后缀（**W**eb**A**ssembly **t**ext format）如果你真的想要的话，也可以手写 `.wat` 文件。以上面的乘法运算为例，我们可以抽象出一个函数，像这样：

```
(module
  (func $mul (param $factor1 i32) (param $factor2 i32) (result i32)
    local.get $factor1
    local.get $factor2
    i32.mul)
  (export "mul" (func $mul))
)
```

### 二进制表示法

使用文件扩展名 `.wasm` 的二进制格式不适合人类阅读，更不适合人类手动创建。使用类似 [wat2wasm](https://webassembly.github.io/wabt/demo/wat2wasm/) 这样的工具，可以将上述代码转换为以下二进制格式。(注释通常不是 `.wasm` 文件的一部分，这里的注释是由 wat2wasm 工具添加的，以便我们更好地理解代码）。

```assembly
0000000: 0061 736d                             ; WASM_BINARY_MAGIC
0000004: 0100 0000                             ; WASM_BINARY_VERSION
; section "Type" (1)
0000008: 01                                    ; section code
0000009: 00                                    ; section size (guess)
000000a: 01                                    ; num types
; func type 0
000000b: 60                                    ; func
000000c: 02                                    ; num params
000000d: 7f                                    ; i32
000000e: 7f                                    ; i32
000000f: 01                                    ; num results
0000010: 7f                                    ; i32
0000009: 07                                    ; FIXUP section size
; section "Function" (3)
0000011: 03                                    ; section code
0000012: 00                                    ; section size (guess)
0000013: 01                                    ; num functions
0000014: 00                                    ; function 0 signature index
0000012: 02                                    ; FIXUP section size
; section "Export" (7)
0000015: 07                                    ; section code
0000016: 00                                    ; section size (guess)
0000017: 01                                    ; num exports
0000018: 03                                    ; string length
0000019: 6d75 6c                          mul  ; export name
000001c: 00                                    ; export kind
000001d: 00                                    ; export func index
0000016: 07                                    ; FIXUP section size
; section "Code" (10)
000001e: 0a                                    ; section code
000001f: 00                                    ; section size (guess)
0000020: 01                                    ; num functions
; function body 0
0000021: 00                                    ; func body size (guess)
0000022: 00                                    ; local decl count
0000023: 20                                    ; local.get
0000024: 00                                    ; local index
0000025: 20                                    ; local.get
0000026: 01                                    ; local index
0000027: 6c                                    ; i32.mul
0000028: 0b                                    ; end
0000021: 07                                    ; FIXUP func body size
000001f: 09                                    ; FIXUP section size
; section "name"
0000029: 00                                    ; section code
000002a: 00                                    ; section size (guess)
000002b: 04                                    ; string length
000002c: 6e61 6d65                       name  ; custom section name
0000030: 01                                    ; name subsection type
0000031: 00                                    ; subsection size (guess)
0000032: 01                                    ; num names
0000033: 00                                    ; elem index
0000034: 03                                    ; string length
0000035: 6d75 6c                          mul  ; elem name 0
0000031: 06                                    ; FIXUP subsection size
0000038: 02                                    ; local name type
0000039: 00                                    ; subsection size (guess)
000003a: 01                                    ; num functions
000003b: 00                                    ; function index
000003c: 02                                    ; num locals
000003d: 00                                    ; local index
000003e: 07                                    ; string length
000003f: 6661 6374 6f72 31            factor1  ; local name 0
0000046: 01                                    ; local index
0000047: 07                                    ; string length
0000048: 6661 6374 6f72 32            factor2  ; local name 1
0000039: 15                                    ; FIXUP subsection size
000002a: 24                                    ; FIXUP section size
```

### 编译为 WebAssembly

正如我们刚刚看到的，`.wat` 和 `.wasm` 都不太适合人类直接使用，这就是 [Emscripten](https://emscripten.org/) 这样的编译器发挥作用的地方。它可以让你将 C 和 C++ 等高级语言编译为 WebAssembly。此外，还有 Rust 等其他语言的编译器。以下面的 C 代码为例：

```c
#include <stdio.h>

int main() {
  printf("Hello World\n");
  return 0;
}
```

通常，你会用 `gcc` 编译器来编译这个 C 程序：

```bash
$ gcc hello.c -o hello
```

[安装 Emscripten ](https://emscripten.org/docs/getting_started/downloads.html)之后，你可以通过 `emcc` 命令，使用几乎相同的参数来编译出 WebAssembly 程序：

```bash
$ emcc hello.c -o hello.html
```

这将创建 `hello.wasm` 文件和 HTML 文件 `hello.html`。打开 `hello.html`，在控制台中你可以看到 `"Hello World"` 字符串被打印了出来。

我们也可以编译出对应的 JS 文件：

```bash
$ emcc hello.c -o hello.js
```

和刚刚一样，这行命令会创建一个 `hello.wasm` 文件，还有一个 `hello.js` 文件，而不是 HTML 文件。我们可以用 Node.js 来运行这个文件：

```bash
$ node hello.js
Hello World
```

## 了解更多

本文对 WebAssembly 的简要介绍只是冰山一角。有关 WebAssembly 的更多信息，请参阅 MDN 的 [WebAssembly 文档](https://developer.mozilla.org/docs/WebAssembly)和 [Emscripten 文档](https://emscripten.org/docs/index.html)。说实话，使用 WebAssembly 可能有点像 "如何画猫头鹰"（[一个外网 meme](https://knowyourmeme.com/memes/how-to-draw-an-owl)），毕竟前端工程师通常对于 C 之类的语言比较不熟悉。幸运的是，我们有像 [StackOverflow 的 `webassembly` 标签](https://stackoverflow.com/questions/tagged/webassembly)这样的频道，如果你友好地进行提问，这里的大佬们会很乐意帮助你。
