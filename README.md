# `optics-tools` for FOXSI-4  <span>&#129418;</span>

A repository to store all software tools for the optics system used for the FOXSI-4 mission.

**See below on contributing to the repository.**

**Note:** FOXSI-1, -2, and -3 used a completely different system that is very different from FOXSI-4. Therefore, this repository may only appropriate for FOXSI-4.

## Repository Aim

This repository will hopefully contain all code that proves useful in the working/analysis of optics (at least from FOXSI-4). Several languages might be used and so the top level will be to contain language specific packages.

For example, the `optics-tools-py` folder will be a Python package containing all the necessary `.py` files. If other languages are to be included, like `IDL`, then a folder called `optics-tools-idl` should be created and used to contain all the `IDL`-ness of the repository. This standard can be applied to the inclusion of other languages (e.g., C++ as `optics-tools-cpp`, etc.).

Every `optics-tools-<?>` folder should have an "examples" and a "tests" folder. The "examples" folder is a great place to include scripts that show how some of the code in the repository works and the "tests" folder is a fantastic place to put code that tests the tools that have been created.

Additionally, there is also an "examples" and "tests" folder in the top level of the repository so there is a place for anything that fits these folders that spans across code from multiple languages.

## Contributing to the repository

Thank you so much for considering to contribute to the repository! <span>&#127881;</span>

In order to contribute, we ask that you first create your own fork of the repository and then clone that fork to your local machine. Branches of your new fork can be created to develop new features or fix bugs (exciting!). When you are happy with the code in that new branch, a pull request (PR) can be opened which aims to merge the code in your fork's branch into the `main` `foxsi/optics-tools` repository. A lot of discussion can be facilitated in an open PR.

**Note:** We aim to _never_ `push` and `pull` from a local machine to this repository directly. If this happens then it can be very difficult for other contributers to understand what changes are being made and how it affects their own PRs. _If the repository is pushed to directly, in order to help track changes and make them visible to other contributers, the repository will be reverted back to it's state before the push and the undone changes will be asked to be proposed via a PR to then be merged._

## The `external` directory

The `external` directory is a place for software external to the repository. There is no guarentee that it will follow any specific coding language and so it would perhaps not be ideal to place it in a specific coding language `tools` directory. Some may be [`git` submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

To clone submodules when cloning the main repository, try the following:

- `git clone --recurse-submodules https://github.com/foxsi/optics-tools.git`

## The `context-information` directory

This directory contains context information that can be shared between a lot of different scripts. E.g., instead of hard coding values, etc., they can be stored here and used numerous times.
