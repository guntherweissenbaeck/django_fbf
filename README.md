# The Fallen Birdy Form

## Throw old database
In case you've got an preexisting database, delete it and do the following:

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

## Add Test Data
To add testdata, use the loaddata functionality of django:

```bash
python3 manage.py loaddata fixtures/data.json
```

## Test Account
The test account you can use:

- user: admin
- password: abcdef

