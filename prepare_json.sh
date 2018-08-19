# prepare_json.sh
# * wrapper to call code that generates json for server to return

# switch pwd context for model.py
cd ./modelgen
python3 ./code/model.py
