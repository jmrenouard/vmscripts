SECRET_PASSWORD="Admin2024_"

create_secrets:
	[ -d "secrets" ] ||mkdir secrets
	echo "$(SECRET_PASSWORD)" > secrets/mysql-root-password
	echo "[client]\nhost=127.0.0.1\nuser=root\npassword=$(SECRET_PASSWORD)" > ${HOME}/.my.cnf
	mkdir -p ${HOME}/.cassandra
	rm -f ${HOME}/.cassandra/cqlshrc
	echo "[authentication]\n#username=\n#password=\n[connection]\nhostname=127.0.0.1\nport=9042" > ${HOME}/.cassandra/cqlshrc
	chmod 600 ${HOME}/.cassandra/cqlshrc

enable_pf:
	sudo sysctl -w net.ipv4.ip_forward=1
	sudo sysctl -w net.ipv6.conf.all.forwarding=1
	 
start_mysql: enable_pf
	 docker run --name mysql -d \
	 -p 3306:3306 \
	 -e MYSQL_ROOT_PASSWORD_FILE=/run/secrets/mysql-root-password \
	 -v $(shell pwd)/secrets:/run/secrets \
	 -v mysql:/var/lib/mysql \
	 --restart unless-stopped \
	 mysql:latest

start_mariadb: enable_pf
	 docker run --name mariadb -d \
	 -p 3307:3306 \
	 -e MYSQL_ROOT_PASSWORD_FILE=/run/secrets/mysql-root-password \
	 -v $(shell pwd)/secrets:/run/secrets \
	 -v mariadb:/var/lib/mysql \
	 --restart unless-stopped \
	 mariadb:latest

start_mariadb106: enable_pf
	 docker run --name mariadb106 -d \
	 -p 3308:3306 \
	 -e MYSQL_ROOT_PASSWORD_FILE=/run/secrets/mysql-root-password \
	 -v $(shell pwd)/secrets:/run/secrets \
	 -v mariadb106:/var/lib/mysql \
	 --restart unless-stopped \
	 mariadb:10.6

start_mysql57: enable_pf
	 docker run --name mysql57 -d \
	 -p 3309:3306 \
	 -e MYSQL_ROOT_PASSWORD_FILE=/run/secrets/mysql-root-password \
	 -v $(shell pwd)/secrets:/run/secrets \
	 -v mysql57:/var/lib/mysql \
	 --restart unless-stopped \
	 mysql:5.7

start_cassandra311:
	docker run --name cassandra311 \
	--network cassandra311 \
	-d \
	-v cassandra311:/var/lib/cassandra \
	-p 9042:9042 \
	-p 7199:7199 \
	-e CASSANDRA_SEEDS='' \
	-e CASSANDRA_NUM_TOKENS=8 \
	-e CASSANDRA_DC=DC1 \
	-e CASSANDRA_RACK=RAC1 \
	-e CASSANDRA_CLUSTER_NAME=CAS311 \
	cassandra:3.11 


start_all: start_mysql start_mariadb start_mariadb106

stop_mysql:
	docker stop mysql
	docker rm -f mysql
stop_mysql57:
	docker stop mysql57
	docker rm -f mysql57 

stop_mariadb:
	docker stop mariadb
	docker rm -f mariadb

stop_mariadb106:
	docker stop mariadb106
	docker rm -f mariadb106

stop_cassandra311:
	docker stop cassandra311
	docker rm -f cassandra311

stop_all: stop_mysql stop_mariadb stop_mariadb106

log_mysql:
	docker logs -f mysql

log_mysql57:
	docker logs -f mysql57

log_mariadb:
	docker logs -f mariadb

log_mariadb106:
	docker logs -f mariadb106

log_cassandra311:
	docker logs -f cassandra311

list_containers:
	docker ps -a | grep -E '(mysql|mariadb|cassandra)'

cleanup_mysql:
	docker volume rm -f mysql

cleanup_mysql57:
	docker volume rm -f mysql57
cleanup_mariadb:
	docker volume rm -f mariadb

cleanup_mariadb106:
		docker volume rm -f mariadb106

cleanup_cassandra311:
	docker volume rm -f cassandra311

cleanup_all: cleanup_mysql cleanup_mysql57 cleanup_mariadb cleanup_mariadb106 cleanup_cassandra311

ps:
	docker ps -a

test_db:
	echo "* Testing access to Databases"
	[ -d "test_db" ] ||	git clone https://github.com/datacharmer/test_db.git

inject_mysql: test_db
	echo "* Injecting MySQL data"
	cd test_db && mysql<employees.sql
	cd test_db/sakila && mysql<./sakila-mv-schema.sql
	cd test_db/sakila && mysql<./sakila-mv-data.sql

inject_mariadb: test_db
	echo "* Injecting MySQL data"
	cd test_db &&	mysql -P 3307<employees.sql
	cd test_db/sakila && mysql -P 3307<./sakila-mv-schema.sql
	cd test_db/sakila && mysql -P 3307<./sakila-mv-data.sql

inject_mariadb106: test_db
	echo "* Injecting MySQL data"
	cd test_db && mysql -P 3308<employees.sql
	cd test_db/sakila && mysql -P 3308<./sakila-mv-schema.sql
	cd test_db/sakila && mysql -P 3308<./sakila-mv-data.sql

inject_all: inject_mysql inject_mariadb inject_mariadb106