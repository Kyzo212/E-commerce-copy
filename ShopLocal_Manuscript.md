# ShopLocal: A Web-Based Local E-Commerce Platform

**A Project Manuscript**

---

**Submitted by:** [Your Name]  
**Course:** [Your Course]  
**Institution:** [Your School/University]  
**Date:** May 1, 2026

---

## Table of Contents

1. Abstract  
2. Problem Statement  
3. Objectives of the Project  
4. Introduction  
5. Core Components  
6. Process: System Workflow and Data Flow  
7. Technology: Tools and System Infrastructure  
8. Scope and Limitations  
9. System Overview and Related Concepts  
10. System Architecture  
11. System Modules  
12. System Implementation  
13. User Interface Description  
14. Conclusion  

---

## Abstract

This project explores the design and implementation of **ShopLocal**, a web-based local e-commerce platform that supports product browsing, cart management, checkout, and order tracking. The system was developed to provide a simple and responsive online shopping experience for customers while giving administrators tools to manage products, users, and orders efficiently.

The platform uses a lightweight Python web stack with server-side rendering, a relational database, and session-based authentication. It also supports role-based access control so that administrators, sellers, and customers have different capabilities. The study emphasizes usability, accessibility, and practical business workflow in a local e-commerce setting.

---

## Problem Statement

Despite the growing use of online shopping platforms, many small local sellers still face difficulties in managing products, processing orders, and providing a smooth shopping experience. Customers, on the other hand, often encounter websites that are difficult to use, lack secure authentication, or do not provide convenient cart and checkout features.

This project aims to address the following questions:

1. How can a local e-commerce platform provide a simple and organized online shopping experience?
2. What features are needed to support customer purchasing, seller participation, and administrator management?
3. How can the system ensure usability, accessibility, and role-based control?

---

## Objectives of the Project

### A. General Objective
To design and develop a web-based e-commerce system called **ShopLocal** for local product browsing, ordering, and management.

### B. Specific Objectives
- To create a responsive website for browsing and purchasing products
- To implement secure user registration and login
- To separate admin, seller, and customer access using role-based permissions
- To allow users to request seller access during registration
- To require admin approval before seller access is activated
- To provide a persistent shopping cart that works without login
- To support product image uploads and inventory management
- To develop order tracking and admin order monitoring features

---

## Introduction

A. In today’s digital environment, e-commerce has become one of the most practical ways for businesses to reach customers. It allows buyers to browse products, compare prices, and place orders from any location with internet access.

B. Many local businesses, however, still struggle with creating online systems that are easy to use and maintain. Some platforms are too complex, while others lack essential features such as authentication, product management, cart handling, and order processing.

C. To address these concerns, this project proposes **ShopLocal**, a web-based e-commerce platform designed for convenience, accessibility, and efficient management. The system aims to help local sellers present their products online while giving customers a smooth and reliable shopping experience.

---

## Core Components

### A. People: Roles and Responsibilities in the System

The system relies on the participation of different users:

- **Administrator**: Responsible for managing products, approving seller requests, managing users, monitoring orders, and maintaining overall system operations.
- **Seller**: A user whose request has been approved by an administrator; manages product listings and related sales activities.
- **Customer**: Browses products, adds items to the cart, places orders, and views order history.

Each role contributes to the smooth operation of the platform and helps maintain an organized shopping environment.

### B. Process: System Workflow and Data Flow

The system follows a structured workflow to support shopping and management operations:

1. **User Registration and Seller Request**  
   Users create accounts and may optionally request seller access during registration.

2. **Admin Review and Approval**  
   Administrator reviews pending seller requests and approves eligible accounts.

3. **Product Browsing**  
   Customers browse products by category or search keyword.

4. **Cart Management**  
   Items can be added, updated, or removed from the shopping cart.

5. **Checkout and Order Creation**  
   Customers review their selected items and submit orders for processing.

6. **Order Storage and Tracking**  
   Orders and order items are stored in the database for future reference.

7. **Administrative Monitoring**  
   Administrators review orders, update order status, and manage active users, seller requests, and products.

### C. Technology: Tools and System Infrastructure

The system uses the following technologies:

1. **Web-Based Interface**  
   The platform is accessed through a web browser.

2. **Database Management System**  
   A relational database is used to store users, sellers, admins, products, orders, and order items.

3. **Backend Framework**  
   The application uses Python with a lightweight server-side architecture.

4. **Frontend Framework and Styling**  
   HTML, JavaScript, Bootstrap, and custom CSS are used to create a responsive and user-friendly interface.

5. **File Upload Handling**  
   Product images can be uploaded and stored in the server’s static directory.

---

## Scope and Limitations

### A. Scope
- The system is a web-based e-commerce platform
- It supports product browsing, cart management, checkout, and order tracking
- It includes registration, login, profile management, and admin functions
- It provides product, user, and seller management for administrators and sellers

### B. Limitations
- The system is limited to the current inventory stored in the database
- Payment processing is not integrated with a real external payment gateway
- Delivery and logistics are not managed directly by the platform
- Seller tools are focused on product management and do not include advanced analytics or settlement features
- Seller access requires manual approval from an administrator
- The platform is intended for a single local deployment rather than a large-scale enterprise setup

---

## System Overview and Related Concepts

### A. E-Commerce Systems

E-commerce systems enable the online buying and selling of products. They typically include product listings, user accounts, shopping carts, checkout workflows, and order history features.

### B. Role-Based Access Control

Role-based access control is a security approach where permissions depend on the user’s role. In this project, customers and administrators have different access levels.

### C. Persistent Shopping Cart

A persistent cart allows users to store selected items even without logging in. In ShopLocal, the cart is stored in a browser cookie so users can continue shopping across page visits.

### D. Order Snapshotting

When an order is created, the system saves a snapshot of the product name and price in the order items table. This ensures that order records remain accurate even if product details change later.

---

## System Architecture

ShopLocal follows a client-server architecture:

- **Frontend**: Browser-based user interface rendered with templates
- **Backend**: Python application logic, authentication, cart handling, order processing, and seller management
- **Database**: Relational database storing users, sellers, products, orders, and order items
- **Static File Storage**: Server directory for uploaded product images

This architecture keeps the system modular and easy to maintain. The database now includes separate profile tables for approved sellers and administrators, which makes role-specific management clearer and easier to extend.

---

## System Modules

### 1. User Module
- Registration
- Login and logout
- Profile management
- Password update

### 2. Product Module
- Product listing
- Product details
- Product creation, editing, and deletion
- Product category filtering
- Product image upload

### 3. Cart Module
- Add to cart
- Update quantity
- Remove item
- Persistent cookie-based cart storage

### 4. Checkout Module
- Review selected items
- Create order record
- Clear cart after purchase

### 5. Order Management Module
- Customer order history
- Order detail view
- Admin order listing
- Admin order status updates

### 6. Seller Module
- Seller request submission during registration
- Admin approval of seller access
- Seller account management
- Seller product listing management
- Seller-specific product ownership
- Monitoring of seller-related inventory and sales

### 7. Administration Module
- User listing
- Seller request review and approval
- Seller listing
- User activation and deactivation
- Order monitoring
- Product and seller management permissions

---

## System Implementation

### Technologies Used

- **Frontend**: HTML, JavaScript, Bootstrap, and custom CSS
- **Backend**: Python and Werkzeug-based routing
- **Database**: SQLAlchemy ORM with a relational database
- **Authentication**: Session cookie with password hashing
- **File Handling**: Local image upload storage

### Key Implementation Details

- The application uses server-side rendered templates.
- Authentication is handled using hashed passwords and session cookies.
- Admin-only actions are protected by role checks.
- Seller access is granted only after admin approval.
- Cart data is stored in a browser cookie in JSON format.
- Order creation stores item snapshots to preserve historical accuracy.
- Uploaded product images are saved in a dedicated static folder.

---

## User Interface Description

The system provides a clean and responsive interface with the following pages:

- Homepage with featured products
- Product catalog with search and category filtering
- Product detail page
- Shopping cart page
- Checkout page
- Login and registration pages
- User profile page
- Order history page
- Seller dashboard pages for managing listings
- Admin order, seller-request, and user management pages

The interface is designed to work on both desktop and mobile devices, with navigation elements that remain accessible across screen sizes.

---

## Conclusion

### A. Summary of Key Points

This project focuses on **ShopLocal**, a web-based local e-commerce platform designed to support product browsing, cart management, checkout, seller approval, and order administration. The system addresses the need for a simple and efficient online shopping platform for customers, sellers, and administrators. It uses role-based access, persistent cart storage, and structured order management to provide a practical e-commerce workflow.

### B. Significance and Value

ShopLocal is valuable because it provides a usable online selling platform for local businesses and a convenient shopping experience for customers. It improves accessibility, simplifies order management, and supports a clear separation of responsibilities between customers, sellers, and administrators. The system also demonstrates how a lightweight web application can solve a real business need.

### C. Final Thoughts

As local businesses continue to move online, platforms like ShopLocal show how web technology can be used to support practical commerce needs. With further improvements such as payment gateway integration, inventory alerts, delivery tracking, and richer seller workflow automation, the system can become even more useful and scalable in the future.

---

*End of Manuscript*
