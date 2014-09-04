# Odoo Sentry connector

an Odoo V8.0 module that connects your odoo deployment with [sentry](https://www.getsentry.com)

## Installation

### Configure a sentry project

first you need to [install](http://sentry.readthedocs.org/en/latest/) Sentry or [buy](https://www.getsentry.com/pricing/) a hosted service from them.

login to your sentry account and create new project, go to project settings and copy `dsn` *data source name*.
open your Odoo config file and put a new config option `sentry_client_dsn` equal to dsn of your project.

now restart odoo server and install `odoo_sentry` module.

go to your sentry project and open `Stream` tab, you will see a message titled *Starting Odoo Server*. congratulation.


### License
This project is licensed under [AGPL v3](http://www.gnu.org/licenses/agpl-3.0.html) (the same as odoo).

