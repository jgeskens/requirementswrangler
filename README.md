requirementswrangler
====================

Small tool for managing your pip/virtualenv requirements

Features:

  * Update your requirements.txt file automatically after working on some libraries your project depends on, by using the "rw.py requirements.txt [package1 [package2 [...]]]" command
  * Update your environment interactively after pulling in a new requirements.txt file, by using the "rw.py sync -i requirements.txt" command.

Usage example:

```bash
(mvne)$ python rw.py ../mvne-platform/deployment/requirements.txt cl_payments provider_ogone
provider_ogone 1d263f84 [up to date]
cl_payments 2f51a0d5 -> a12345bc
```

Make sure your virtualenv is active while running this command.
