cd /var/www/oneshotauto/oneshotauto
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart myproject
sudo systemctl restart nginx