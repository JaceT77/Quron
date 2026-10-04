export PATH := justfile_directory() + "/.venv/bin:" + env_var('PATH')

run:
    uv run quron

pybabel_extract:
    pybabel extract -k _:1,1t -k _:1,2 -k __ --input-dirs=. -o locales/messages.pot

pybabel_init lang:
    pybabel init -i locales/messages.pot -d locales -D messages -l {{lang}}

pybabel_compile:
    pybabel compile -d locales -D messages

pybabel_update:
    pybabel update -d locales -D messages -i locales/messages.pot

pybabel_init_all:
    pybabel init -i locales/messages.pot -d locales -D messages -l en
    pybabel init -i locales/messages.pot -d locales -D messages -l ru
    pybabel init -i locales/messages.pot -d locales -D messages -l uz

pybabel:
    pybabel extract -k _:1,1t -k _:1,2 -k __ --input-dirs=. -o locales/messages.pot
    pybabel update -d locales -D messages -i locales/messages.pot
    pybabel compile -d locales -D messages
