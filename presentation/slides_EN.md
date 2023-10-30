---
title: Template
separator: <!--h-->
verticalSeparator: <!--v-->
theme: dracula
revealOptions:
  auto-animate: true
---

## Présentation Template

Note: authors : 
 - S.LAVAZAIS

sources:
 - [Wikipedia - software performance testing](https://en.wikipedia.org/wiki/Software_performance_testing)
 - 
<!--v-->

## Introduction - Sommaire

1. What is performance test?
2. Test with Blazemeter Taurus
3. Element 3

Note:

1. What is performance testing?
2. What kind of tests?
   1. isolation testing
   2. load testing
   3. stress testing
   4. spike testing
   5. breakpoint testing
   6. soaking testing
3. Test with Blazemeter Taurus
4. Demo
5. Thanks!

<!--h-->

### What is performance testing?

<img src="img/what-is-perf-1.png" alt="drawing" width="500"/>

Note:
Performance testing is the ability to put an application, with all its dependencies, in a "real-life" or a virtual 
context and observe how they behave.
<!--v-->

### What is performance testing?

<div>
responses over time<br/>
<img src="img/what-is-perf-response-time.jpeg" alt="drawing" width="300"/>
</div>

Note:
Performance testing provides direct and non-direct benefits such as:
 - responses over time (direct)
 - ressources utilization (direct)
 - capacity to adapt / scalability (direct)
 - prevent downtime (non-direct)
 - detecting uncovered bugs / bottleneck (non-direct)
 - mitigate security breach (non-direct)
<!--v-->

### Element 2

Note:
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Sem fringilla ut morbi tincidunt augue interdum velit euismod in. Elit ullamcorper dignissim cras tincidunt lobortis feugiat vivamus at.

<!--v-->

<!-- .slide: data-auto-animate -->
### Element 3

```json[|2|3|4]
{
  "branches": [
    "main",
    {
      "name": "pre-*",
      "prerelease": true
    }
  ]
}
```

Note:
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Sem fringilla ut morbi tincidunt augue interdum velit euismod in. Elit ullamcorper dignissim cras tincidunt lobortis feugiat vivamus at.
