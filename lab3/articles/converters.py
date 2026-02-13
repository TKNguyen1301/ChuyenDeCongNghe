"""
Custom path converters cho URL patterns
"""


class FourDigitYearConverter:
    """Converter cho năm 4 chữ số"""
    regex = '[0-9]{4}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%04d' % value


class MonthConverter:
    """Converter cho tháng (01-12)"""
    regex = '(0[1-9]|1[0-2])'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%02d' % value


class UsernameConverter:
    """Converter cho username (chỉ chữ, số và underscore)"""
    regex = '[a-zA-Z0-9_]+'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)
