# prepare_json.sh
# LEGACY - replaced by direct module call
# * wrapper to call code that generates json for server to return

# switch pwd context for model.py
cd /modules/modelgen
python3 ./code/model.py
