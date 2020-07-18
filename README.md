Простой текстовый браузер. Умеет печатать контент сайтов и сохранять кэш. Браузер запускается через коммандную строку. Нужно ввести команду:

python browser.py dir_for_cash

Где dir_for_cash - название директории, куда вы хотите сохранять кэш

Доступные опции:
	1. Открыть сайт. Для этого нужно просто ввести адрес, например google.com или 		https://vk.com
	2. Вернуться на предыдущую страницу, для этого нужно написать "back"
	3. Выйти из браузера, для этого надо написать "exit"

Все просмотренные сайты сохраняются в кэш. После просмотра сайта, можно посмотреть его еще раз, используя краткий адрес и не делая запрос. Например, краткий адрес https://www.google.com - google.

Можно вернуться на прошлую страницу, используя опцию back. Например, если вы сначала посетили google.com, потом github.com и нажали back, то браузер покажет google.com. Если после этого зашли на vk.com и нажали back, о браузер покажет github.com

Весь текст, который является ссылкой, программа покрасит в синий
