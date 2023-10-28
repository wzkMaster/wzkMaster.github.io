---
title: "[译] Node.js Worker Thread 与 Child Process 对比"
date: 2023-10-25
comments: true
description:
tags: ["JavaScript"]
---

> 原文链接: <https://dev.to/amplication/nodejs-worker-threads-vs-child-processes-which-one-should-you-use-178i>
>
> 原文作者：[Muly Gottlieb](https://dev.to/mulygottlieb)

并行处理在需要大量计算的应用中发挥着至关重要的作用。考虑一个确定给定数字是否为质数的应用程序。我们从 1 到该数字的平方根进行遍历，才能确定它是否是质数，如果数字比较大的话，这类操作非常耗时且计算量极大。

如果你在 Node.js 上构建这类需要大量 CPU 计算的应用，就会长时间阻塞主线程的运行。由于 Node.js 的单线程特性，不涉及 I/O 的大量计算操作将导致应用程序停止运行，直到计算完成。

因此，我们通常认为 Node.js 不适合用来创建 CPU 密集型的应用程序。不过，Node.js 引入了 Worker Threads（工作者线程）和 Child Processes（子进程）的概念，使得 Node.js 能够进行并行处理，从而能够并行地执行特定进程。在本文中，我们将了解这两个概念，并讨论在不同情况下如何在他们之间做出选择。

## Worker Threads

### 什么是 Node.js 中的 Worker Threads?

Node.js 能够高效处理 I/O 操作。但是，当它遇到 CPU 密集型的操作时，就会导致主线程的事件循环冻结。

![](https://res.cloudinary.com/practicaldev/image/fetch/s--2E968psn--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_800/https://static-assets.amplication.com/blog/nodejs-worker-threads-vs-child-processes-which-one-should-you-use/0.png)

当 Node.js 遇到异步操作时，它会将该操作放到线程池中。但是，当需要运行计算量大的操作时，它会在主线程上执行，这将导致应用程序阻塞，直到操作完成。为了缓解这一问题，Node.js 引入了 Worker Threads（工作者线程）的概念，从而使得主线程不必执行计算密集型的操作，这样开发人员就能以无阻塞的方式并行生成多个线程。

Worker Thread 会启动一个独立的 Node.js 上下文，该上下文包含自己的 Node.js 运行时、事件循环和事件队列，并在一个远程 V8 环境中运行。它在与主线程的事件循环断开的环境中运行，使主线程的事件循环得以释放。

![](https://res.cloudinary.com/practicaldev/image/fetch/s--w0k8CVcc--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_800/https://static-assets.amplication.com/blog/nodejs-worker-threads-vs-child-processes-which-one-should-you-use/1.png)

如上图所示，Node.js 创建了多个独立的运行时作为 Worker Threads，其中每个线程都独立于其他线程执行，并通过消息通道（message channel）向父线程传递信息。此时父线程可以像往常一样继续执行（而不会被阻塞）。这样，你就实现了在 Node.js 中进行多线程编程。

### 在 Node.js 中使用 Worker Threads 的好处是什么？

显然，使用 Worker Thread 对 CPU 密集型的应用程序有很大的好处，它有如下几个优点：

1. 提高程序性能：它将繁重的计算操作从主线程转移到 Worker Thread 上，这样就可以释放主线程，让应用程序的响应速度更快，为更多的请求提供服务。

2. 提高并行性：如果您有一个大型进程，希望将其分割成多个子任务并行执行，就可以使用 Worker Thread 来实现。例如，如果你要检查 1,999,3241,123 是否是质数，就可以使用多个 Worker Thread 来检查一定范围内的除数（在 WT1 中为 1 到 100,000，在 WT2 中为 100,001 到 200,000，等等），这会大大加快计算的速度。

### 什么时候应该使用 Worker Thread?

> 仔细想想，你应该只在运行与主线程独立的大量计算时使用 Worker Thread

在 Worker Thread 中运行 I/O 操作是没有意义的，因为这些操作已经交给了事件循环。因此，只有当需要在隔离的环境中进行计算量大的操作时，再考虑使用工作线程。

### 如何在 Node.js 中创建 Worker Thread?

如果上面所说的吸引了你的话，让我们来看看如何在 Node.js 中使用 Worker Thread。代码如下：

```js
const {
  Worker,
  isMainThread,
  parentPort,
  workerData,
} = require("worker_threads");

const { generatePrimes } = require("./prime");

const threads = new Set();
const number = 999999;

const breakIntoParts = (number, threadCount = 1) => {
  const parts = [];
  const chunkSize = Math.ceil(number / threadCount);

  for (let i = 0; i < number; i += chunkSize) {
    const end = Math.min(i + chunkSize, number);
    parts.push({ start: i, end });
  }

  return parts;
};

if (isMainThread) {
  const parts = breakIntoParts(number, 5);
  parts.forEach((part) => {
    threads.add(
      new Worker(__filename, {
        workerData: {
          start: part.start,
          end: part.end,
        },
      })
    );
  });

  threads.forEach((thread) => {
    thread.on("error", (err) => {
      throw err;
    });
    thread.on("exit", () => {
      threads.delete(thread);
      console.log(`Thread exiting, ${threads.size} running...`);
    });
    thread.on("message", (msg) => {
      console.log(msg);
    });
  });
} else {
  const primes = generatePrimes(workerData.start, workerData.end);
  parentPort.postMessage(
    `Primes from - ${workerData.start} to ${workerData.end}: ${primes}`
  );
}
```

上面的代码段展示了一个可以使用 Worker Thread 的理想场景。要创建 Worker Thread，需要从 `worker_threads` 库中导入 `Worker`、`IsMainThread`、`parentPort` 和 `workerData`，它们将被用于创建工作线程。

在上面的代码中，我创建了一个算法，用于查找给定范围内的所有质数。它在主线程中将该范围分割成不同部分（在例子中是五个部分），然后使用 `new Worker()` 创建多个 Worker Thread 来处理每个部分。Worker Thread 将执行 else 代码块，在分配给该 Worker Thread 的范围内查找质数，最后使用 `parentPort.postMessage()` 将结果发送回父（主）线程。

## Node.js 子进程

### 什么是 Node.js 中的子进程（Child Process）

子进程不同于 Worker Thread。Worker Thread 在同一个进程中提供一个隔离的事件循环和 V8 运行时，而子进程则是整个 Node.js 运行时的独立实例。每个子进程都有自己的内存空间，并通过消息流或管道（或文件、数据库、TCP/UDP 等）等 IPC（inter-process communication, 进程间通信）技术与主进程通信。

### 在 Node.js 中使用子进程的好处是什么？

在 Node.js 中使用子进程有以下几个好处：

1. 提升隔离性：每个子进程都在自己的内存空间中运行，与主进程隔离。这对于可能存在资源冲突或依赖关系需要分离的任务非常有利。

2. 提升可扩展性：利用子进程，我们能够将任务分配给多个进程，从而利用多核系统的优势，处理更多并发请求。

3. 增强鲁棒性：如果子进程由于某种原因崩溃了，主进程仍然能够正常运行。

4. 运行外部程序：通过子进程，我们可以将外部程序或脚本作为独立进程运行。这在需要与其他可执行文件交互的情况下非常有用。

### 什么时候应该在 Node.js 中使用子进程？

现在，我们已经了解了子进程带来的好处。除此之外，了解在 Node.js 中何时应该使用子进程也非常重要。根据我的经验，我建议你在 Node.js 中执行外部程序时使用子进程。

我最近的一次经历是，我想在我的 Node.js 服务中运行一个外部可执行文件。而在主线程内直接执行二进制文件是不可能的。因此，我不得不使用一个子进程来执行外部二进制文件。

### 如何在 Node.js 中创建子进程？

现在，有趣的部分来了。我们要如何创建子进程？在 Node.js 中创建子进程有几种方法（你可以使用 `spawn()`、`fork()`、`exec()` 和 `execFile()` 等方法），建议阅读[文档](https://nodejs.org/api/child_process.html)以了解全貌，下面的代码展示了创建子进程最简单的一种方法：

```js
const { spawn } = require("child_process");
const child = spawn("node", ["child.js"]);

child.stdout.on("data", (data) => {
  console.log(`Child process stdout: ${data}`);
});

child.on("close", (code) => {
  console.log(`Child process exited with code ${code}`);
});
```

只需要从 `child_process` 模块中导入 `spawn()` 方法，然后将一个 CLI 及其参数作为参数传递即可。在我们的示例中，我们运行了一个名为 `child.js` 的文件。

文件执行过程中打印的日志会通过 `stdout` 事件流输出，而 `close` 事件回调则会在进程结束运行时被执行。

当然，这只是使用子进程的一个非常简单的例子，主要是为了说明它的概念。

## 如何在 Worker Thread 和子进程中作出选择？

现在我们已经知道了什么是子进程和 Worker Thread，那么了解何时使用这两种技术就很重要了。它们都不是适用于所有情况的银弹，应该根据具体情况进行选择。

### 在这些情况下使用 Worker Thread:

1. 你需要运行 CPU 密集型任务。如果你的任务是 CPU 密集型的，Worker Thread 是一个好选择。
2. 你的任务需要线程之间的共享内存和高效交流。Worker Thread 内置了对共享内存和用于交流的通信系统的支持。

### 在这些情况下使用子进程：

1. 你要运行的任务需要相互隔离并独立运行，尤其是当涉及外部程序时。每个子进程都在自己的内存空间中运行。
2. 你需要使用 IPC 机制（如标准输入/输出流、消息传递或事件）在进程间进行通信。子进程非常适合这一目的。

## 小结

并行计算是现代系统设计的一个重要方面，尤其是在构建处理超大数据集或计算密集型任务的应用程序时。在使用 Node.js 构建此类应用程序时，必须考虑使用 Worker Thread 或者子进程。

如果你的系统设计不当，没有采用正确的并行处理技术，系统可能会因过度消耗资源而表现不佳（因为生成这些线程/进程也会消耗大量资源）。

因此，软件工程师和架构师必须根据实际情况，参考本文提供的信息来选择合适的工具。

此外，你也可以使用 [Amplication](https://amplication.com/) 这样的工具来快速创建 Node.js 应用程序，从而专注于开发并行处理功能，而不必浪费时间为 Node.js 服务（重新）构建所有模板代码。
