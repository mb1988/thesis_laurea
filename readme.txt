PROVA

Modifiche per il deployment su Heroku
=====================================

0) modificare la sezione '[paths]' di .hg/hgrc mettendoci le due righe

	defaults = ssh://hg@bitbucket.org/tesisti_santini/tesi-asl
	heroku = git+ssh://git@heroku.com:asl-mi.git

   avendo cura di configurare la ssh aggiungendo al file ~/.ssh/config
   ad esempio

	Host heroku.*
		User git
		HostName heroku.com
		IdentityFile ~/.ssh/CHIAVE_PER_HEROKU
		IdentitiesOnly yes

   dove al posto di CHIAVE_PER_HEROKU va messo il percorso di una delle chiavi
   attualmente configurate su heroku che sono:

   	ssh-rsa AAAAB3NzaC...Zx4MeQyw== Borriero
	ssh-rsa AAAAB3NzaC...sM2LdmYCgr borry@ubuntu
	ssh-rsa AAAAB3NzaC...yNISzF+1fB santini@asl

1) creare in questa directory un file di nome .env che contenga

	DATABASE_URL= ... qui va l'URL del databse ...
	PORT=8000
	STACKATO_FILESYSTEM=/tmp

2) creare un ambiente virtuale con virtualenv ed installare le librerie con

	pip install -r requirements.txt

   questo punto si può omettere se le librerie sono già disponibili.

3) testare in locale l'applicazione, per popolare il db (la prima volta) fare

	. ./setenv
	python manage.py setup

   mentre per eseguire l'applicazione (ogni volta) fare

   	. ./setenv
   	python run.py

 4) se va in locale, fare 'hg commit' e quindi 'hg push heroku'


Credenziali
===========

Per entrare nell'applicazione sono stati creati due profili base
un profilo da amministratore con username admin e password password
un profilo utente con username guest e password password


Creazione documenti
==============

Per creare i documenti dal file JSON eseguire da terminale 
python create.py
