requirementswrangler
====================

Small tool to update your requirements.txt file automatically

Usage example:

```bash
(mvne)$ python rw.py ../mvne-platform/deployment/requirements.txt cl_payments provider_ogone
provider_ogone 1d263f84 [up to date]
cl_payments 2f51a0d5 -> a12345bc
```

Make sure your virtualenv is active while running this command.
