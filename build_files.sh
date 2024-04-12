# build_files.sh

pip install -r requirements.txt
python3.10 manage.py collectstatic --noinput
python3.10 manage.py migrate --noinput
