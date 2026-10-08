# Method Writing Guide

## Goal

Write Method clearly by mapping the actual technical pipeline into a sequence a reader can reproduce.

## Pre-Writing Questions

For every module:

1. How does it run?
2. Why is it needed?
3. Why should it work?

## Three Elements of a Module

### 1. Motivation

State the problem or limitation that requires the module.

### 2. Module Design

Describe the representation/network/data structure and the forward process:

`input -> step 1 -> step 2 -> step 3 -> output`

### 3. Technical Advantage

Explain why this design should help, and connect the explanation to measurable behavior where possible.

## Writing Order

1. Sketch the pipeline figure.
2. Map the sketch to Method subsections.
3. Plan motivation/design/advantage for each subsection.
4. Write the concrete module design first.
5. Add motivation and advantages afterward.

## Clarity Checks

- Every paragraph has one message.
- The first sentence identifies the paragraph role.
- The reason for each important operation is understandable.
- Key terms and notation do not change names across sections.
- Implementation details are placed where a reader can find them without interrupting the main story.
