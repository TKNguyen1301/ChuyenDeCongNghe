# 📚 Django Model Indexes - Complete Guide

## 🎯 Tổng quan về Django Indexes

Django Indexes là công cụ mạnh mẽ để tối ưu hóa hiệu suất database bằng cách tạo các cấu trúc dữ liệu đặc biệt giúp tăng tốc độ truy vấn.

### 🏗️ **Các loại Indexes trong Django**

## 1. 📋 **Simple Field Indexes (B-Tree)**

Indexes cơ bản trên một field duy nhất - phổ biến nhất và hiệu quả cho equality và range queries.

```python
class Article(models.Model):
    status = models.CharField(max_length=20)
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            Index(fields=['status']),           # Single field
            Index(fields=['category']),         # Single field
            Index(fields=['created_at']),       # Time-based queries
        ]
```

**✅ Tốt cho:**
- WHERE status = 'published'
- WHERE created_at > '2024-01-01'
- ORDER BY created_at

## 2. 🔗 **Composite/Multi-column Indexes**

Indexes trên nhiều fields - rất hiệu quả cho queries filter nhiều điều kiện.

```python
class Meta:
    indexes = [
        # Composite indexes
        Index(fields=['status', 'category']),
        Index(fields=['category', '-created_at']),  # Descending order
        Index(fields=['status', '-published_at', 'is_featured']),
    ]
```

**✅ Tốt cho:**
- WHERE status = 'published' AND category = 'tech'
- WHERE category = 'tech' ORDER BY created_at DESC
- Leftmost prefix rule áp dụng

**📝 Lưu ý:** Thứ tự fields quan trọng - leftmost prefix rule!

## 3. 🎯 **Partial Indexes (Conditional)**

Indexes chỉ áp dụng cho subset của data thỏa mãn điều kiện WHERE.

```python
class Meta:
    indexes = [
        # Chỉ index published articles
        Index(
            fields=['title', 'slug'],
            condition=Q(status='published'),
            name='published_articles_idx'
        ),
        
        # Chỉ index high-rating articles
        Index(
            fields=['rating'],
            condition=Q(rating__gte=4.0),
            name='high_rating_articles_idx'
        ),
        
        # Multiple conditions
        Index(
            fields=['view_count'],
            condition=Q(view_count__gt=1000) & Q(is_featured=True),
            name='popular_featured_articles_idx'
        ),
    ]
```

**✅ Ưu điểm:**
- Nhỏ hơn (ít storage)
- Nhanh hơn (ít data scan)
- Tối ưu cho business logic

## 4. ⚡ **Functional Indexes (Expression-based)**

Indexes trên kết quả của functions/expressions thay vì raw field values.

```python
from django.db.models.functions import Lower, Upper, Length, Coalesce

class Meta:
    indexes = [
        # Case-insensitive title search
        Index(
            Lower('title').desc(),
            name='lower_title_idx'
        ),
        
        # Content length analysis
        Index(
            Length('content'),
            name='content_length_idx'
        ),
        
        # Popularity score calculation
        Index(
            F('view_count') * F('rating'),
            name='popularity_score_idx'
        ),
        
        # Complex expression
        Index(
            Upper('category'),
            Coalesce('published_at', 'created_at'),
            name='category_publish_date_idx'
        ),
    ]
```

**✅ Tốt cho:**
- Case-insensitive searches
- Computed values
- Mathematical calculations
- NULL handling

## 5. 📦 **Covering Indexes (PostgreSQL only)**

Indexes bao gồm additional non-key columns để tránh table lookups.

```python
class Meta:
    indexes = [
        # Covering index với include
        Index(
            fields=['status'],
            include=['title', 'created_at'],
            name='status_covering_idx'
        ),
        
        # Multiple fields + includes
        Index(
            fields=['category', 'status'],
            include=['title', 'summary', 'view_count'],
            name='category_status_covering_idx'
        ),
    ]
```

**✅ Ưu điểm:**
- Index-only scans
- Không cần access table
- Rất nhanh cho SELECT specific fields

**⚠️ Hạn chế:**
- Chỉ PostgreSQL
- SQLite sẽ ignore include columns

## 6. 📊 **E-commerce Optimization Examples**

```python
class Product(models.Model):
    class Meta:
        indexes = [
            # Basic e-commerce queries
            Index(fields=['is_active']),
            Index(fields=['category']),
            Index(fields=['price']),
            
            # Complex business queries
            Index(fields=['is_active', 'category', '-price']),
            Index(fields=['brand', 'category', '-created_at']),
            
            # Partial indexes cho business logic
            Index(
                fields=['price', 'stock_quantity'],
                condition=Q(is_active=True) & Q(stock_quantity__gt=0),
                name='available_products_idx'
            ),
            
            # Functional indexes cho calculations
            Index(
                F('price') * (100 - F('discount_percentage')) / 100,
                name='final_price_idx'
            ),
        ]
```

## 🚀 **Performance Testing Results**

Từ script test của chúng ta:

```
📰 ARTICLE QUERIES
1. Simple status filter:          ⏱️  17.18ms | 🔍 1 queries
2. Composite filter:              ⏱️  4.29ms  | 🔍 1 queries  
3. Partial index query:           ⏱️  1.75ms  | 🔍 1 queries
4. Functional index query:        ⏱️  2.56ms  | 🔍 1 queries
5. Complex multi-condition:       ⏱️  1.19ms  | 🔍 1 queries

🛍️ PRODUCT QUERIES  
1. E-commerce filter:             ⏱️  1.08ms  | 🔍 1 queries
2. Price range filter:            ⏱️  1.48ms  | 🔍 1 queries
3. Bestsellers (partial):         ⏱️  0.80ms  | 🔍 1 queries
4. Brand + Category:              ⏱️  0.57ms  | 🔍 1 queries
```

## 📝 **Best Practices**

### ✅ **DOs:**

1. **Index commonly filtered fields**
   ```python
   Index(fields=['status', 'is_active', 'created_at'])
   ```

2. **Use composite indexes for multi-field queries**
   ```python
   Index(fields=['category', 'status', '-created_at'])
   ```

3. **Partial indexes cho filtered subsets**
   ```python
   Index(fields=['price'], condition=Q(is_active=True))
   ```

4. **Functional indexes cho case-insensitive search**
   ```python
   Index(Lower('title'), name='case_insensitive_title')
   ```

### ❌ **DON'Ts:**

1. **Không index mọi field** - indexes cần storage và maintenance
2. **Không duplicate indexes** - Django sẽ warn về redundant indexes  
3. **Tên index dài >30 chars** - Database limitations
4. **Quá nhiều indexes** - Slow down INSERT/UPDATE operations

## 🔧 **Index Management Commands**

```bash
# Tạo migrations cho indexes
python manage.py makemigrations

# Áp dụng migrations
python manage.py migrate

# Check indexes (custom command)
python manage.py dbshell
.indices  # SQLite
\di       # PostgreSQL
```

## 📊 **Database-specific Features**

### **PostgreSQL** 🐘
- ✅ Covering indexes (INCLUDE)
- ✅ Partial indexes 
- ✅ Functional indexes
- ✅ GIN, GiST, Hash indexes
- ✅ Expression indexes

### **SQLite** 🗃️
- ✅ Basic B-Tree indexes
- ✅ Partial indexes (limited)
- ⚠️ Functional indexes (limited)
- ❌ Covering indexes (ignored)

### **MySQL** 🐬
- ✅ Basic indexes
- ✅ Composite indexes  
- ❌ Partial indexes
- ⚠️ Functional indexes (8.0.13+)

## 🎯 **Real-world Use Cases**

### **1. Blog/CMS System**
```python
# Articles với status filtering, category browsing, time-based queries
Index(fields=['status', 'category', '-published_at'])
Index(fields=['author', '-created_at'])
Index(condition=Q(status='published'), fields=['slug'])
```

### **2. E-commerce Platform**
```python
# Products với availability, pricing, categorization
Index(fields=['is_active', 'category', '-price'])
Index(condition=Q(is_active=True) & Q(stock__gt=0), fields=['price'])
Index(F('price') * (100 - F('discount'))/100, name='final_price')
```

### **3. Analytics/Logging**
```python
# Logs với time-based queries, error monitoring
Index(fields=['-timestamp', 'level'])
Index(condition=Q(level__in=['error', 'critical']), fields=['-timestamp'])
Index(fields=['module', 'function'])
```

## 📈 **Monitoring & Optimization**

1. **Sử dụng Django Debug Toolbar** để xem queries
2. **EXPLAIN ANALYZE** để analyze query plans
3. **Monitor slow queries** trong production
4. **Index usage statistics** để optimize

## 🎉 **Kết luận**

Django Indexes là công cụ không thể thiếu để:
- ⚡ Tăng tốc độ queries đáng kể
- 📊 Optimize database performance  
- 🎯 Hỗ trợ business logic hiệu quả
- 🔍 Cải thiện user experience

**💡 Key takeaway:** Hiểu rõ query patterns của ứng dụng để tạo indexes phù hợp!

---

📚 **Tài liệu tham khảo:**
- [Django Model Indexes](https://docs.djangoproject.com/en/5.2/ref/models/indexes/)
- [Database Performance](https://docs.djangoproject.com/en/5.2/topics/db/optimization/)
- [PostgreSQL Indexes](https://www.postgresql.org/docs/current/indexes.html)
