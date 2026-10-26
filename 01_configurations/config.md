# dbt and PostgreSQL Local Configurations

For the **Digital Literacy EU Capstone Project** I set up `dbt` and `PostgreSQL` locally. The purpose of this setup is to process similar `.csv` and `.tsv` data files from Eurostat in the same manner, creating a powerful transformation instrument with `dbt`.  Here are the main steps I took to create this setup locally.

---
### `PostgreSQL` Local Setup
1. Install the latest version off PostgreSQL locally (run in terminal):      

    `brew install postgresql`

    It will automatically create a PostgreSQL database called `postgres` with a user name as the current Mac username and with empty password.

For more information, check relevant [documentation](https://wiki.postgresql.org/wiki/Homebrew).

2. To create a new database for a particular project use `psql` commands (or see below).



--- 
### `dbt postgres` Local Setup

1. Create a new environment for a `dbt` project:
``` bash
conda info --envs # to check existing envs
conda create --yes --name dbt_project python=3.9 # to create a new env
```
The follwing terminal commands are used to activate/deactivate the environment:  
``` bash
conda activate dbt_project  # activates
conda deactivate # deactivates, goes back to base
```

In the current setup the environment management is performed by `miniconda` and the environment location is `/opt/miniconda3/envs/dbt_project`.

In case some updates are needed, the following command can be used:  
`conda update -n base -c defaults conda`

2. Install `dbt-postgres`:  
`pip install dbt-postgres`  
Documentation on `dbt-postgres` is provided on [official website](https://docs.getdbt.com/docs/local/connect-data-platform/postgres-setup?version=1.12_).

3. After installing, start PostgreSQL database:
`brew services start postgresql@18 # control for the version installed!`

You can check the status, running:
`brew services list`:
if start was successful, you will see a list (with at least one instance of a database) and it's status will be `started` (green):
```
| Name | Status | User | File |
| --- | --- | --- | --- |
| `postgresql@18` | started | `[username]` | `~/Library/.../sh.brew.postgresql@18.list` |
```

5. Test if dbt works locally:  
`dbt init dbt_test_project`  
where `dbt_test_project` is ust a name of a folder `dbt` will create to keep the project files together. Initiation of   `dtb` also automatically starts creation of multople sub-folders (e.g., seed, models, test, etc) and `.yaml` files.

6. In order to create a connection between `dbt` and `PostgreSQL`, I needed to provide information about the database I will use. For this capstone peoject, I use a locally set PostgreSQL database: 
    * type of database:  
        > [1] (PostgreSQL)
    * host:
        > localhost
    * port:
        > 5432 (default)
    * username:
        > [your username]
    * pass:
        > [your pass]
    * dbname:
        > postgres
    * schema:
        > public
    * threads:
        > 6

To check the connection, terminal will offer to run `dbt debug`. For successfull test, the user's working directory has to match the folder created for the project.

5. For a better user exeperience and access to specific `dbt` features (like lineage and others), I installed `Visual Code dbt extension`:
- Go to the left side bar > `Extensions`
- Select `Power User for dbt`
- Trust and Install
**- Don't forget to SELECT PROPER INTERPRETER!!!**
> In case one forgot to select proper interpreter for the **Power User for dbt** extension:
> * select correct env + select correct interpreter (see below) in Command Palette (`Cmd + Shift + P`--> Python: Select Interpreter);
> * call Command Palette again `Cmd + Shift + P`;
> * type **Power User for dbt: Detect Python from terminal**
> * when asked to confirm the Python detected in terminal -- confirm. Done.

6. Configurate a new database for the project:
- `psql --version` to check if the `psql` is there
- `psql -U <username>` connect to PostgreSQL (admin user) > opens console (you can type commands in SQL directly in terminal when the line starts with prefix `postgres=#`)
- run `CREATE DATABASE <name>;`
- check that is was created: `\l` 
- make a connection in `DBeaver` to double-check;
- to leave editing more, type `\q` in terminal.

7. Connect the `dbt-postgres` (local version) to the new PostgreSQL database:
- go to the Home folder (~/.dbt)
- find file `profiles.yaml`
- change the credentials inside (e.g., database name).

If when you open the project repository again, and VS Code (or another EDA) throws an error and marks `.yaml` project file as un-executable, select a different interpreter (the one which has access to `dbt-postgres` installed). Find command `Select Interpreter` and choose one from the conda environment with the libraries installed (in this case -- `dbt_project` coda env). How:
* `Cmd + Shift + P` (for Mac) --> entering Command Palette
* type and select **Python: Select Interpreter**
* select the one with environment for dbt project (in this setup -- `dbt_project`).

Nota Bene: Every time, if one needs to check if there is a PostgreSQL database running, check the status with `brew services list`. If a running service needs to be stopped: `brew services stop postgresql`, and started again: `brew services start postgresql`.

