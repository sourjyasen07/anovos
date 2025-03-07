<p align="center">
<a href="https://anovos.ai"><img src="https://mobilewalla-anovos.s3.amazonaws.com/images/anovos-dark-horizontal.png" alt="anovos-dark-horizontal" border="0"></a>
</p>

# Anovos

[![release](https://img.shields.io/badge/release-alpha%200.1-yellowgreen?style=plastic)](https://github.com/anovos/anovos/releases)
[![Docs Latest](https://img.shields.io/badge/docs-latest-blue.svg?style=plastic)](https://docs.anovos.ai/)
[![License](https://img.shields.io/badge/License-Apache_2.0-red.svg?style=plastic)](https://opensource.org/licenses/Apache-2.0)
[![twitter](https://img.shields.io/badge/Follow--lightgrey?logo=twitter&style=social)](https://twitter.com/ml_anovos)
[![Slack](https://img.shields.io/badge/slack-join_chat-white.svg?logo=slack&style=social)](https://go.mlops.community/slack)


_Anovos_ is an open source library for feature engineering at scale.
Built by data scientist for the data science community, it provides all capabilities required for data ingestion and transformation.

Leveraging the power of [Apache Spark](https://spark.apache.org/) behind the scenes, _Anovos_ improves data scientists' productivity
and helps them build more resilient and better performing models.

# Quick Start

The easiest way to try out _Anovos_ and explore its capabilities is through the provided
[examples](/examples) that you can run via Docker without the need to install anything on your local machine:

```bash
# clone the Git repository
git clone https://www.github.com/anovos/anovos.git
cd anovos/examples

# generate the Docker image (including Apache Spark and a Jupyter environment)
./create_anovos_examples_docker_image.sh

# Launch an anovos-examples Docker container
sudo docker run -p 8888:8888 anovos-examples:latest
```

To reach the Juypter environment, 
open the link to `http://127.0.0.1:8888/?token...` generated by the Jupyter NotebookApp.

If you're not familiar with _Anovos_ or feature engineering, the _Getting Started with Anovos_ guide is a good
place to begin your journey. You can find it in the `guides` folder within the Jupyter environment.

For more detailed instructions, see the [examples README](/examples/README.md).

# Using Anovos

## Requirements

To use _Anovos_, you need a compatible version of [Apache Spark](https://spark.apache.org/).

Currently, we support:
- Apache Spark 2.4.x (on Java 8)
- Python 3.7.x

Please note that _Anovos_ is not yet compatible with Apache Spark 3.x or later versions of Python.
For a more detailed and comprehensive description of the Spark environment expected by _Anovos_, please see [here](https://docs.anovos.ai/using-anovos/setting-up/locally.html).

## Installation

You can install the latest release of _Anovos_ directly through [PyPI](https://pypi.org/project/anovos/):  

```bash
pip install anovos
```

## Documentation

We provide a comprehensive documentation at [docs.anovos.ai](https://docs.anovos.ai).

For usage examples, see the provided [interactive guides and Jupyter notebooks](/examples) as well as the [Spark demo](/demo).

# Overview

<p align="center">
  <img src="https://mobilewalla-anovos.s3.amazonaws.com/images/anovos_architecture.png" width="830px" alt="Anovos Architecture Diagram">
</p>

## Roadmap

_Anovos_ is still in the early stages of its development.
To see what's planned for the upcoming releases, see our [roadmap](https://docs.anovos.ai/using-anovos/roadmap.html).

## Development Version

To try out the latest additions to _Anovos_, you can install it directly from _GitHub_:  

```bash
pip install git+https://github.com/anovos/anovos.git
```

Please note that this version is frequently updated and might not be fully compatible with the documentation available at [docs.anovos.ai](https://docs.anovos.ai).

# Contribute

We're always happy to discuss and accept improvements to _Anovos_.
To get started, please refer to our [Contributing to Anovos](https://docs.anovos.ai/community/contributing.html) page in the documentation.
