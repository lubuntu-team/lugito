=======
History
=======

0.1.0 (20th May 2018)
----------------------

* Initial Release


0.2.0 (21st November 2018)
---------------------------

* added functionality for reporting creation, comments and edits on comments of
  diffs
* Refactored into Python package
* irc and launchpad connections written into separate Python modules
* corrected issues with reporting using links with anchors via IRC
* added some unittests

* **Still TODO**

  * Documentation - read the docs
  * Add decorators to Lugito class to check that a request has been validated before other tasks can be completed
  * Improve test coverage
  * Pypi upload
  * Add exceptions in the event that connector send method calls are not executed correctly
  * CI and automated docs and Pypi udpate
  * in-situ testing