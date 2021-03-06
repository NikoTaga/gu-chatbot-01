# gu-chatbot-01

GeekPython01 Shop Bot - бот для работы на социальных платформах с Bot API
в качестве каталога магазина и средства продажи и оплаты товаров через платёжные системы.
Имплементирован на языке Python в виде приложения под фреймворк Django.

Поддерживает платформы Одноклассники и JivoSite, а также платёжные системы PayPal и Stripe.

## Порядок настройки.

После деплоя на сервер требуется указать следующие переменные окружения:

1. Для работы с платформой Одноклассники:

    * **OK_TOKEN** - ключ для работы с подключённой группой, получается в настройках сообщений группы

2. Для работы с платформой JivoSite (подключение производится через службу поддержки, ссылка для связи формируется на основе двух частей):

    * **JIVO_WH_KEY** - ключ, устанавливаемый со стороны платформы JivoSite, первая часть ссылки
    * **JIVO_TOKEN** - ключ, устанавливаемый со стороны бот-оператора, вторая часть ссылки

3. Для работы с платёжной системой PayPal:

    * **PAYPAL_CLIENT_ID**, **PAYPAL_CLIENT_SECRET** - ключи получаются в настройках приложений разработчика PayPal
    * **PAYPAL_WEBHOOK_ID** - получается при создании вебхука в настройках приложения разработчика PayPal (вебхуку требуются два события - Checkout order approved, Payment capture completed)

4. Для работы с платёжной системой Stripe:

    * **STRIPE_PUBLIC_KEY**, **STRIPE_SECRET_KEY** - ключи получаются в настройках приложений разработчика Stripe
    * **PAYPAL_WEBHOOK_ID** - получается при создании вебхука в настройках приложения разработчика Stripe
    * **SITE_HTTPS_URL** - веб-адрес сервера в формате https:// - необходимо для минимальной функциональности Stripe - создания редиректа и страницы подтверждения оплаты.
