import time


def publication_density(timestamp_list: list) -> dict:
    """
    Функция определения плотности публикаций группы постов по их timestamp
    :param timestamp_list: список timestamp постов
    :return: словарь, содержащий плотность публикации постов по времени суток
    """
    density = {"night": 0, "morning": 0, "afternoon": 0, "evening": 0}

    # количество постов для подсчета плотности публикаций
    total_posts = len(timestamp_list)

    # пробегаем по каждому timestamp поста
    for timestamp in timestamp_list:

        # получаем час публикации из timestamp поста
        post_hour_publish = int(time.ctime(timestamp).split()[3].split(':')[0])

        # проверяем в каком часу был сделан пост и увеличиваем соответствующее значение счетчика
        if post_hour_publish < 6:
            density["night"] += 1
        elif 6 <= post_hour_publish < 12:
            density["morning"] += 1
        elif 12 <= post_hour_publish < 18:
            density["afternoon"] += 1
        else:
            density["evening"] += 1

    # считаем плотность публикаций
    # for key in density:
    #     density[key] = round((density[key] * 100)/total_posts)

    # вуаля
    return density
