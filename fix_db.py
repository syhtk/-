with open('analytics_module.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
with open('analytics_module.py', 'w', encoding='utf-8') as f:
    for line in lines:
        if 'total_sessions =' in line and 'conn.cursor().execute' in line:
            f.write('    cursor = conn.cursor()\n    cursor.execute("SELECT COUNT(*) FROM reviews_log")\n    row_a = cursor.fetchone()\n    total_sessions = row_a[0] if row_a else 0\n')
        elif 'total_coupon =' in line and 'conn.cursor().execute' in line:
            f.write('    cursor.execute("SELECT SUM(coupon_issued) FROM reviews_log")\n    row_b = cursor.fetchone()\n    total_coupon = float(row_b[0]) if (row_b and row_b[0] is not None) else 0.0\n')
        elif 'angry_count =' in line and 'conn.cursor().execute' in line:
            f.write('    cursor.execute("SELECT COUNT(*) FROM reviews_log WHERE user_emotion IN (\'Angry\', \'Disappointed\')")\n    row_c = cursor.fetchone()\n    angry_count = row_c[0] if row_c else 0\n')
        else:
            f.write(line)
