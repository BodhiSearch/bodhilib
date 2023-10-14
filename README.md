# bodhilib
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/BodhiSearch/bodhilib/blob/main/LICENSE)
![pypi](https://img.shields.io/pypi/v/bodhilib.svg)
[![CI/CD](https://github.com/BodhiSearch/bodhilib/actions/workflows/core.yml/badge.svg)](https://github.com/BodhiSearch/bodhilib/actions/workflows/core.yml)
[![Documentation Status](https://readthedocs.org/projects/bodhilib/badge/?version=stable&style=default)](https://bodhilib.readthedocs.io/en/stable/)
[![codecov](https://codecov.io/gh/BodhiSearch/bodhilib/branch/main/graph/badge.svg?token=EXFQHNBA9Z)](https://codecov.io/gh/BodhiSearch/bodhilib/)

Bodhilib is a pluggable and extensible LLM framework.

Currently the popular LLM framework tends to do everything by themselves, resulting in extraordinary bloat,
Bodhilib is built on top of a plugin architecture, with a very thin core implementing the most
critical LLM related operations. Rest of the features and variations are provided by plugins.
