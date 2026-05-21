import pandas as pd
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

def get_insights(recs):
    if not recs: 
        return "Нет данных для анализа."
    
    df = pd.DataFrame(recs)

    m = df['mood'].mean()
    w = df['work_hours'].mean()
    s = df['sleep_hours'].mean()
    

    if len(df[df['sleep_hours'] >= 7.5]) > 0 and len(df[df['sleep_hours'] < 7.5]) > 0:
        hs = df[df['sleep_hours'] >= 7.5]['mood'].mean()
        ls = df[df['sleep_hours'] < 7.5]['mood'].mean()
        sm = " Сон > 7.5ч улучшает настроение!" if hs > ls else " Сон слабо влияет на настроение."
    else:
        sm = "Недостаточно данных о сне для сравнения."
    

    if len(df[df['work_hours'] >= 4]) > 0 and len(df[df['work_hours'] < 4]) > 0:
        hw = df[df['work_hours'] >= 4]['mood'].mean()
        lw = df[df['work_hours'] < 4]['mood'].mean()
        wm = "Много работы снижает настроение." if lw > hw else "Работа не ухудшает настроение."
    else:
        wm = "Недостаточно данных о работе для сравнения."
    
    return (f" **Средние показатели:**\n"
            f"Настроение: {m:.1f}/5\n"
            f"Работа: {w:.1f} ч\n"
            f"Сон: {s:.1f} ч\n\n"
            f" **Инсайты:**\n{sm}\n{wm}")

def create_chart(recs, fn='chart.png'):
    df = pd.DataFrame(recs)
    if df.empty: 
        return None
    
    plt.figure(figsize=(10, 5))
    

    df['date_dt'] = pd.to_datetime(df['date'])
    
    plt.plot(df['date_dt'], df['mood'], 'o-', label='Настроение', color='green', lw=2)
    plt.plot(df['date_dt'], df['work_hours'], 's--', label='Работа (ч)', color='blue', lw=2)
    plt.plot(df['date_dt'], df['sleep_hours'], '^-', label='Сон (ч)', color='orange', lw=2)
    
    plt.xlabel('Дата')
    plt.ylabel('Значение')
    plt.title('Тренды самочувствия')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    plt.savefig(fn, dpi=150, bbox_inches='tight')
    plt.close()
    return fn