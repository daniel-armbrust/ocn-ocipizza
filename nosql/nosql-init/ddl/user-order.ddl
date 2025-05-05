CREATE TABLE IF NOT EXISTS user.order ( 
    order_id INTEGER,             
    address JSON,
    pizza JSON,  
    total NUMBER,
    order_datetime INTEGER,
    status ENUM(PREPARING,OUT_FOR_DELIVERY,DELIVERED,CANCELED) DEFAULT PREPARING,             
PRIMARY KEY (order_id))