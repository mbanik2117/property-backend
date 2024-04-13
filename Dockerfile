FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .  

# Assuming your web server (e.g., Nginx) is exposed at port 80
EXPOSE 80  

# Link entrypoint.sh to the container
COPY entrypoint.sh .

# Set permissions for entrypoint.sh to be executable
RUN chmod +x entrypoint.sh

# Set the default command to run entrypoint.sh
CMD ["/app/entrypoint.sh"] 
