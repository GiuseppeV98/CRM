FROM python:3.10  
WORKDIR /var/app/crm 
COPY . ./ 
RUN mv .env.test .env
RUN pip install -r requirements.txt
EXPOSE 8080
CMD [ "python", "./manage.py", "runserver", "0.0.0.0:8080" ]