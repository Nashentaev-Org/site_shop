import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# --- Модели данных (Pydantic) ---
# Эти модели определяют структуру данных, которые мы будем отправлять и получать

class Product(BaseModel):
    id: int
    name: str
    price: float
    oldPrice: Optional[float] = None
    category: str
    image: str
    rating: float
    reviews: int
    sizes: List[str]
    colors: List[str]
    badge: Optional[str] = None
    description: str = "Подробное описание товара скоро появится здесь."
    specifications: Dict[str, str] = {"Материал": "100% хлопок"}

class PromoRequest(BaseModel):
    code: str

class PromoResponse(BaseModel):
    code: str
    discount_type: str  # 'percent' or 'fixed'
    value: float

class OrderItem(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    size: str
    color: str

class Order(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: str
    delivery: str
    payment: str
    items: List[OrderItem]
    totalAmount: float
    # Можно добавить и другие поля из формы, например, адрес
    city: Optional[str] = None
    street: Optional[str] = None

class Feedback(BaseModel):
    firstName: str
    email: str
    subject: str
    message: str


# --- Инициализация FastAPI ---

app = FastAPI(
    title="Fashion Store API",
    description="Бэкенд API для интернет-магазина одежды",
    version="1.0.0"
)

# --- CORS Middleware ---
# Это позволяет вашему HTML-сайту (frontend) общаться с этим сервером (backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешает доступ со всех источников
    allow_credentials=True,
    allow_methods=["*"],  # Разрешает все методы (GET, POST, etc.)
    allow_headers=["*"],
)

# --- "База данных" (хранится в памяти) ---

all_products = [
    Product(id=1, name='Джинсовая рубашка', price=2999, oldPrice=3999, category='men', image='👔', rating=4.2, reviews=127, sizes=['s', 'm', 'l', 'xl'], colors=['blue', 'black'], badge='-25%', description="Стильная джинсовая рубашка из высококачественного денима. Классический крой, удобная посадка и долговечность.", specifications={"Материал": "100% хлопок", "Крой": "Классический"}),
    Product(id=2, name='Элегантное платье', price=4999, category='women', image='👗', rating=4.8, reviews=89, sizes=['xs', 's', 'm', 'l'], colors=['black', 'red'], badge='NEW', description="Идеальное платье для вечернего выхода. Подчеркивает фигуру и создает утонченный образ.", specifications={"Материал": "Шелк", "Длина": "Миди"}),
    Product(id=3, name='Детская футболка', price=1299, category='kids', image='👕', rating=4.5, reviews=45, sizes=['xs', 's', 'm'], colors=['white', 'blue', 'red'], description="Яркая и удобная футболка для вашего ребенка из натурального хлопка.", specifications={"Материал": "100% хлопок", "Принт": "Машинка"}),
    Product(id=4, name='Мужские джинсы', price=3999, oldPrice=5999, category='men', image='👖', rating=4.6, reviews=203, sizes=['m', 'l', 'xl', 'xxl'], colors=['blue', 'black'], badge='-33%', description="Классические джинсы прямого кроя. Отлично подходят для повседневной носки.", specifications={"Материал": "Деним", "Крой": "Прямой"}),
    Product(id=5, name='Женская блузка', price=2799, category='women', image='👚', rating=4.3, reviews=67, sizes=['xs', 's', 'm', 'l'], colors=['white', 'black'], description="Легкая и воздушная блузка, которая добавит элегантности вашему образу.", specifications={"Материал": "Вискоза", "Рукав": "Длинный"}),
    Product(id=6, name='Детские кроссовки', price=2199, category='kids', image='👟', rating=4.4, reviews=156, sizes=['xs', 's', 'm'], colors=['white', 'blue'], description="Удобные и легкие кроссовки для активных детей.", specifications={"Материал верха": "Текстиль", "Подошва": "Резина"}),
    Product(id=7, name='Мужской пиджак', price=5999, category='men', image='🧥', rating=4.7, reviews=98, sizes=['m', 'l', 'xl'], colors=['black', 'gray'], description="Стильный пиджак для деловых встреч и особых случаев.", specifications={"Материал": "Шерсть", "Крой": "Приталенный"}),
    Product(id=8, name='Женская юбка', price=2299, category='women', image='👗', rating=4.1, reviews=34, sizes=['xs', 's', 'm', 'l'], colors=['black', 'gray'], description="Юбка-карандаш, которая идеально подойдет для офисного дресс-кода.", specifications={"Материал": "Полиэстер", "Длина": "До колена"}),
    Product(id=9, name='Спортивная футболка', price=1599, category='men', image='👕', rating=4.0, reviews=78, sizes=['s', 'm', 'l', 'xl'], colors=['white', 'black', 'blue'], description="Футболка из дышащего материала для занятий спортом.", specifications={"Материал": "Синтетика", "Технология": "Dry-Fit"}),
    Product(id=10, name='Летнее платье', price=3299, category='women', image='👗', rating=4.6, reviews=112, sizes=['xs', 's', 'm', 'l'], colors=['white', 'blue'], description="Легкое платье из натуральных материалов для жаркой погоды.", specifications={"Материал": "Лен", "Длина": "Макси"})
]

valid_promo_codes = {
    'SAVE10': {'type': 'percent', 'value': 10},
    'NEWUSER': {'type': 'percent', 'value': 15},
    'WELCOME': {'type': 'fixed', 'value': 500}
}


# --- API Эндпоинты ---

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в API Fashion Store!"}


@app.get("/api/products", response_model=List[Product])
def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    size: Optional[str] = None,
    color: Optional[str] = None,
    sort: Optional[str] = None  # 'price-low', 'price-high', 'rating'
):
    """
    Получение списка товаров с возможностью фильтрации и сортировки.
    """
    products = all_products[:]  # Копируем список, чтобы не изменять оригинал

    # Фильтрация
    if category and category != 'all':
        products = [p for p in products if p.category == category]
    if search:
        products = [p for p in products if search.lower() in p.name.lower()]
    if min_price:
        products = [p for p in products if p.price >= min_price]
    if max_price:
        products = [p for p in products if p.price <= max_price]
    if size:
        products = [p for p in products if size in p.sizes]
    if color:
        products = [p for p in products if color in p.colors]

    # Сортировка
    if sort == 'price-low':
        products.sort(key=lambda p: p.price)
    elif sort == 'price-high':
        products.sort(key=lambda p: p.price, reverse=True)
    elif sort == 'rating':
        products.sort(key=lambda p: p.rating, reverse=True)

    return products


@app.get("/api/products/{product_id}", response_model=Product)
def get_product_by_id(product_id: int):
    """
    Получение детальной информации о товаре по его ID.
    """
    product = next((p for p in all_products if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product


@app.post("/api/promo/validate", response_model=PromoResponse)
def validate_promo(promo_request: PromoRequest):
    """
    Валидация промокода.
    """
    code_data = valid_promo_codes.get(promo_request.code.upper())
    if not code_data:
        raise HTTPException(status_code=404, detail="Промокод не найден или недействителен")

    return PromoResponse(
        code=promo_request.code.upper(),
        discount_type=code_data['type'],
        value=code_data['value']
    )


@app.post("/api/orders")
def create_order(order: Order):
    """
    Прием и обработка нового заказа.
    """
    print("----------- НОВЫЙ ЗАКАЗ -----------")
    print(f"Имя: {order.firstName} {order.lastName}")
    print(f"Email: {order.email}, Телефон: {order.phone}")
    print(f"Способ доставки: {order.delivery}")
    print(f"Способ оплаты: {order.payment}")
    print("Товары в заказе:")
    for item in order.items:
        print(f" - {item.name} (Размер: {item.size}, Цвет: {item.color}) - {item.quantity} шт. x {item.price}₽")
    print(f"ИТОГО К ОПЛАТЕ: {order.totalAmount}₽")
    print("-----------------------------------")
    
    order_id = "FS" + str(abs(hash(order.email + str(order.totalAmount))))[:6]

    return {"message": "Заказ успешно оформлен!", "order_id": order_id}


@app.post("/api/feedback")
def receive_feedback(feedback: Feedback):
    """
    Прием сообщения из формы обратной связи.
    """
    print("----- НОВОЕ СООБЩЕНИЕ С ФОРМЫ -----")
    print(f"Имя: {feedback.firstName}")
    print(f"Email: {feedback.email}")
    print(f"Тема: {feedback.subject}")
    print(f"Сообщение: {feedback.message}")
    print("-----------------------------------")
    return {"message": "Ваше сообщение успешно отправлено!"}


# --- Запуск сервера ---

if __name__ == "__main__":
    # Команда для запуска: uvicorn backend:app --reload
    uvicorn.run(app, host="127.0.0.1", port=8000)