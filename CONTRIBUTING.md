# Contributing to *niflexlogger-automation-python* 

Contributions to *niflexlogger-automation-python* are welcome from all!

*niflexlogger-automation-python* is managed via [git](https://git-scm.com), with the canonical upstream
repository hosted on [GitHub](https://github.com/ni/niflexlogger-automation-python/).

*niflexlogger-automation-python* follows a pull-request model for development.  If you wish to
contribute, you will need to create a GitHub account, fork this project, push a
branch with your changes to your project, and then submit a pull request.

See [GitHub's official documentation](https://help.github.com/articles/using-pull-requests/) for more details.

# Getting Started

To contribute to this project, it is recommended that you follow these steps:

1. Fork the repository on GitHub.
2. Run the unit tests on your system (see Testing section). At this point,
   if any tests fail, do not begin development. Try to investigate these
   failures. If you're unable to do so, report an issue through our
   [GitHub issues page](https://github.com/ni/niflexlogger-automation-python/issues).
3. Write new tests that demonstrate your bug or feature. Ensure that these
   new tests fail.
4. Make your change.
5. Run all the unit tests again (which include the tests you just added),
   and confirm that they all pass.
6. Send a GitHub Pull Request to the main repository's master branch. GitHub
   Pull Requests are the expected method of code collaboration on this project.


# Testing

Before running any tests, a supported version of Python must be installed.
Version 3.6 is preferred, as that version is the most likely to be problematic.
Installing multiple supported python versions is even better.

To install all development dependencies required:
```
$ pip install -r .\requirements.txt
```

Use the `tox` package for running all tests. To get set up:
```
$ pip install tox
```

That should set up virtualenv and let you run tests on all supported environments.
To run all tests, run the following command:
```
$ tox
```
Every time you run that the package will be created and all tests will run.

To run all tests in place with your current python environment setup:
```
$ pytest
```

To only run the tests in one particular folder, run
```
$ pytest tests/myfolder
```

# Developer Certificate of Origin (DCO)

   Developer's Certificate of Origin 1.1

   By making a contribution to this project, I certify that:

   (a) The contribution was created in whole or in part by me and I
       have the right to submit it under the open source license
       indicated in the file; or

   (b) The contribution is based upon previous work that, to the best
       of my knowledge, is covered under an appropriate open source
       license and I have the right under that license to submit that
       work with modifications, whether created in whole or in part
       by me, under the same open source license (unless I am
       permitted to submit under a different license), as indicated
       in the file; or

   (c) The contribution was provided directly to me by some other
       person who certified (a), (b) or (c) and I have not modified
       it.

   (d) I understand and agree that this project and the contribution
       are public and that a record of the contribution (including all
       personal information I submit with it, including my sign-off) is
       maintained indefinitely and may be redistributed consistent with
       this project or the open source license(s) involved.

(taken from [developercertificate.org](https://developercertificate.org/))

See [LICENSE](https://github.com/ni/niflexlogger-automation-python/blob/master/LICENSE)
for details about how *niflexlogger-automation-python* is licensed.
