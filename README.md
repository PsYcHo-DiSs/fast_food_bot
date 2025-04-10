## ENG
### To run the project using Docker ecosystem:

1. **Create a Docker network on the server** by running:
   ```bash
   docker network create fastfood-net
   ```
   
2. **Launch the PostgreSQL database container** (specify the Docker network created above):
   ```bash
   docker run --name db_server_fast_food_bot    --network fastfood-net    -e POSTGRES_PASSWORD=<...your...password...>    -d --restart unless-stopped    postgres
   ```

3. **Clone the repository** to your local machine.

4. **Create your `.env` file** based on the `.env.example` file from the project.

5. **Since both containers will be in the same Docker network, you can refer to the database container by its name:**
   ```
   DB_ADDRESS=db_server_fast_food_bot (this matches the name of the PostgreSQL container above)
   ```

6. **Build the Docker image**:
   ```bash
   docker build -t fastfoodbot ~/fast_food_bot/
   ```

7. **Launch the container based on the image created above** (it will be connected to the shared Docker network):
   ```bash
   docker run --name fast_food_bot    --network fastfood-net    -d --restart unless-stopped    fastfoodbot
   ```

8. **Both containers will start automatically**. The `./database/models.py` file will be executed under the hood, which initializes the database with test data (only the `lavaš` and `donar` categories are populated).


## RU

Для того, чтобы запустить проект, используя Docker экосистему:
1. Создаём докер сеть на сервере, командой -> `docker network create fastfood-net`
2. Запускаем контейнер базы данных postgres (указываем общую докер сеть, созданную выше) ->
    ```
    docker run --name db_server_fast_food_bot \
    --network fastfood-net \
    -e POSTGRES_PASSWORD=<...your...password...> \
    -d --restart unless-stopped \
    postgres
    ```
3. Клонируем репозиторий к себе.
3. Создаём свой файл `.env` на основе файла `.env.example` из проекта.
4. Благодаря последующему нахождению двух контейнеров в одной докер сети, адресом базы данных можно указывать имя контейнера:
   
    ```
    DB_ADDRESS=db_server_fast_food_bot (совпадает с именем контейнера бызы postgres выше)
    ```
6. Билдим образ docker ->
   ```
   docker build -t fastfoodbot ~/fast_food_bot/
   ```
7. Запускаем контейнер на основе выше созданного образа (помещается в общую докер сеть) ->
   ```
   docker run --name fast_food_bot \
    --network fastfood-net \
    -d --restart unless-stopped \
    fastfoodbot
   ```
8. Оба контейнера запускаются автоматически, под капотом происходит инициализация файлика `./database/models.py` в котором база заполняется тестовыми данными (заполнены только сегменты из категорий `лаваш` и `донары`). 
