# ============================================================
# 중고차 판매가격 예측 모델 - 1단계: 탐색적 데이터 분석 (EDA)
# ============================================================

# ────────────────────────────────────────────
# 0. 라이브러리 불러오기
# ────────────────────────────────────────────
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# ── 한글 폰트 설정 ──
# Windows: 맑은 고딕
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

print("✅ 라이브러리 로드 완료")
print(f"  pandas {pd.__version__} / numpy {np.__version__}")

# ────────────────────────────────────────────
# 1. 데이터 불러오기
# ────────────────────────────────────────────
DATA_PATH = r"C:\Users\Admin\hipython\ml\bermuda.project\encar_kia_all\output\encar_feature_processed_with_model_avg_te.csv"
OUTPUT_DIR = r"C:\Users\Admin\hipython\ml\bermuda.project\encar_kia_all\output\eda"

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH, encoding='utf-8-sig')

print(f"\n✅ 데이터 로드 완료: {df.shape[0]:,}행 × {df.shape[1]}열")
print(f"   저장 경로: {OUTPUT_DIR}")

# ────────────────────────────────────────────
# 2. 기본 정보 확인
# ────────────────────────────────────────────
print("\n" + "="*60)
print("【 2-1. 컬럼 목록 및 데이터 타입 】")
print("="*60)
dtype_df = pd.DataFrame({
    '컬럼명': df.columns,
    '데이터타입': df.dtypes.values,
    '결측치수': df.isnull().sum().values,
    '결측치(%)': (df.isnull().sum().values / len(df) * 100).round(2),
    '고유값수': df.nunique().values
})
print(dtype_df.to_string(index=False))

# ────────────────────────────────────────────
# 3. 결측치 확인
# ────────────────────────────────────────────
print("\n" + "="*60)
print("【 2-2. 결측치 요약 】")
print("="*60)
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({'결측치수': missing, '결측치(%)': missing_pct})
missing_df = missing_df[missing_df['결측치수'] > 0].sort_values('결측치수', ascending=False)
if len(missing_df) == 0:
    print("  → 결측치 없음 ✅")
else:
    print(missing_df)

# ────────────────────────────────────────────
# 4. 수치형 변수 기술통계
# ────────────────────────────────────────────
print("\n" + "="*60)
print("【 2-3. 수치형 변수 기술통계 】")
print("="*60)

# 연속형 수치 변수만 선택 (이진형 제외)
binary_cols = [c for c in df.columns if df[c].nunique() == 2 and set(df[c].unique()) <= {0, 1}]
numeric_cols = df.select_dtypes(include='number').columns.tolist()
continuous_cols = [c for c in numeric_cols if c not in binary_cols and c != '매물ID']

desc = df[continuous_cols].describe().T
desc['skewness'] = df[continuous_cols].skew().round(3)
desc['kurtosis'] = df[continuous_cols].kurt().round(3)
print(desc.round(2))

# ────────────────────────────────────────────
# 5. 타겟 변수 분포 시각화
# ────────────────────────────────────────────
print("\n" + "="*60)
print("【 2-4. 타겟 변수 분포: 현재가격_만원 】")
print("="*60)

target = '현재가격_만원'
target_stats = df[target].describe()
print(target_stats)
print(f"\n  왜도(skewness): {df[target].skew():.4f}")
print(f"  첨도(kurtosis): {df[target].kurt():.4f}")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('타겟 변수 분포: 현재가격_만원', fontsize=14, fontweight='bold')

# 원본 분포
axes[0].hist(df[target], bins=80, color='steelblue', edgecolor='white', linewidth=0.3)
axes[0].set_title('원본 분포')
axes[0].set_xlabel('현재가격 (만원)')
axes[0].set_ylabel('빈도')
axes[0].axvline(df[target].mean(), color='red', linestyle='--', label=f'평균 {df[target].mean():.0f}만원')
axes[0].axvline(df[target].median(), color='orange', linestyle='--', label=f'중앙값 {df[target].median():.0f}만원')
axes[0].legend(fontsize=9)

# 로그 변환 분포
log_target = np.log1p(df[target])
axes[1].hist(log_target, bins=80, color='seagreen', edgecolor='white', linewidth=0.3)
axes[1].set_title('로그 변환 분포 (log1p)')
axes[1].set_xlabel('log(현재가격+1)')
axes[1].set_ylabel('빈도')

# 박스플롯
axes[2].boxplot(df[target], vert=True, patch_artist=True,
                boxprops=dict(facecolor='lightblue', color='steelblue'),
                medianprops=dict(color='red', linewidth=2))
axes[2].set_title('박스플롯')
axes[2].set_ylabel('현재가격 (만원)')

plt.tight_layout()
save_path = os.path.join(OUTPUT_DIR, '01_target_distribution.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
plt.show()
print(f"  → 저장: {save_path}")

# ────────────────────────────────────────────
# 6. 연속형 피처 분포 시각화
# ────────────────────────────────────────────
print("\n" + "="*60)
print("【 2-5. 연속형 피처 분포 】")
print("="*60)

plot_cols = [c for c in continuous_cols if c != target]
n = len(plot_cols)
ncols = 3
nrows = (n + ncols - 1) // ncols

fig, axes = plt.subplots(nrows, ncols, figsize=(18, nrows * 4))
axes = axes.flatten()

for i, col in enumerate(plot_cols):
    axes[i].hist(df[col], bins=50, color='cornflowerblue', edgecolor='white', linewidth=0.3)
    axes[i].set_title(col)
    axes[i].set_xlabel(col)
    axes[i].set_ylabel('빈도')
    skew_val = df[col].skew()
    axes[i].text(0.98, 0.95, f'skew={skew_val:.2f}', transform=axes[i].transAxes,
                 ha='right', va='top', fontsize=8, color='red')

# 남은 빈 axes 숨기기
for j in range(i+1, len(axes)):
    axes[j].set_visible(False)

plt.suptitle('연속형 피처 분포', fontsize=14, fontweight='bold')
plt.tight_layout()
save_path = os.path.join(OUTPUT_DIR, '02_continuous_features_dist.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
plt.show()
print(f"  → 저장: {save_path}")

# ────────────────────────────────────────────
# 7. 이진형 피처 비율 확인
# ────────────────────────────────────────────
print("\n" + "="*60)
print("【 2-6. 이진형 피처 비율 (1의 비율 %) 】")
print("="*60)

binary_ratio = (df[binary_cols].mean() * 100).sort_values(ascending=False).round(1)
print(binary_ratio.to_string())

# 시각화
fig, ax = plt.subplots(figsize=(14, 6))
colors = ['steelblue' if v >= 50 else 'salmon' for v in binary_ratio.values]
bars = ax.bar(binary_ratio.index, binary_ratio.values, color=colors, edgecolor='white', linewidth=0.5)
ax.axhline(50, color='gray', linestyle='--', linewidth=1, label='50% 기준선')
ax.set_title('이진형 피처별 1의 비율 (%)', fontsize=13, fontweight='bold')
ax.set_ylabel('비율 (%)')
ax.set_ylim(0, 110)
plt.xticks(rotation=45, ha='right', fontsize=9)

for bar, val in zip(bars, binary_ratio.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{val:.1f}%', ha='center', va='bottom', fontsize=8)

ax.legend()
plt.tight_layout()
save_path = os.path.join(OUTPUT_DIR, '03_binary_features_ratio.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
plt.show()
print(f"  → 저장: {save_path}")

# ────────────────────────────────────────────
# 8. 상관관계 분석
# ────────────────────────────────────────────
print("\n" + "="*60)
print("【 2-7. 타겟과의 상관관계 】")
print("="*60)

corr_with_target = df[numeric_cols].drop(columns=['매물ID']).corr()[target].drop(target)
corr_sorted = corr_with_target.abs().sort_values(ascending=False)
print(corr_with_target[corr_sorted.index].round(4).to_string())

# 상관계수 히트맵 (연속형만)
corr_matrix = df[continuous_cols].corr()

fig, axes = plt.subplots(1, 2, figsize=(18, 7))

# 타겟 상관계수 바 차트
colors_corr = ['steelblue' if v >= 0 else 'salmon' for v in corr_with_target[corr_sorted.index].values]
axes[0].barh(corr_sorted.index, corr_with_target[corr_sorted.index].values,
             color=colors_corr, edgecolor='white')
axes[0].axvline(0, color='black', linewidth=0.8)
axes[0].set_title(f'타겟({target})과의 상관계수', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Pearson 상관계수')

# 전체 히트맵
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            vmin=-1, vmax=1, linewidths=0.5, ax=axes[1], annot_kws={'size': 8})
axes[1].set_title('연속형 변수 상관관계 히트맵', fontsize=12, fontweight='bold')
plt.xticks(rotation=45, ha='right', fontsize=9)
plt.yticks(fontsize=9)

plt.tight_layout()
save_path = os.path.join(OUTPUT_DIR, '04_correlation.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
plt.show()
print(f"  → 저장: {save_path}")

# ────────────────────────────────────────────
# 9. 주요 피처별 타겟 분포 (scatter)
# ────────────────────────────────────────────
print("\n" + "="*60)
print("【 2-8. 주요 피처 vs 타겟 산점도 】")
print("="*60)

key_features = [c for c in continuous_cols if c != target]
n = len(key_features)
ncols = 3
nrows = (n + ncols - 1) // ncols

fig, axes = plt.subplots(nrows, ncols, figsize=(18, nrows * 4))
axes = axes.flatten()

for i, col in enumerate(key_features):
    axes[i].scatter(df[col], df[target], alpha=0.2, s=5, color='steelblue')
    # 추세선
    z = np.polyfit(df[col], df[target], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df[col].min(), df[col].max(), 100)
    axes[i].plot(x_line, p(x_line), 'r-', linewidth=1.5)
    corr_val = df[[col, target]].corr().iloc[0, 1]
    axes[i].set_title(f'{col} (r={corr_val:.3f})', fontsize=10)
    axes[i].set_xlabel(col, fontsize=9)
    axes[i].set_ylabel(target, fontsize=9)

for j in range(i+1, len(axes)):
    axes[j].set_visible(False)

plt.suptitle('주요 피처 vs 타겟 산점도', fontsize=14, fontweight='bold')
plt.tight_layout()
save_path = os.path.join(OUTPUT_DIR, '05_scatter_features_vs_target.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
plt.show()
print(f"  → 저장: {save_path}")

# ────────────────────────────────────────────
# 10. 모델별 가격 분포 (Top 20)
# ────────────────────────────────────────────
print("\n" + "="*60)
print("【 2-9. 모델별 평균 가격 (Top 20) 】")
print("="*60)

model_price = df.groupby('모델')[target].agg(['mean', 'median', 'count']).round(0)
model_price.columns = ['평균가격', '중앙값가격', '매물수']
model_price = model_price.sort_values('평균가격', ascending=False)
print(model_price.head(20).to_string())

top20 = model_price.head(20)
fig, ax = plt.subplots(figsize=(16, 6))
ax.bar(top20.index, top20['평균가격'], color='steelblue', edgecolor='white', label='평균가격')
ax.bar(top20.index, top20['중앙값가격'], color='orange', alpha=0.7, edgecolor='white', label='중앙값가격')
ax.set_title('모델별 평균/중앙값 가격 (Top 20)', fontsize=13, fontweight='bold')
ax.set_ylabel('가격 (만원)')
ax.legend()
plt.xticks(rotation=45, ha='right', fontsize=9)
plt.tight_layout()
save_path = os.path.join(OUTPUT_DIR, '06_model_price_top20.png')
plt.savefig(save_path, dpi=150, bbox_inches='tight')
plt.show()
print(f"  → 저장: {save_path}")

# ────────────────────────────────────────────
# 11. 이상치 확인 (IQR 기준)
# ────────────────────────────────────────────
print("\n" + "="*60)
print("【 2-10. 이상치 탐지 (IQR 기준) 】")
print("="*60)

outlier_summary = []
for col in continuous_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    n_out = ((df[col] < lower) | (df[col] > upper)).sum()
    pct = round(n_out / len(df) * 100, 2)
    outlier_summary.append({'컬럼': col, '하한': round(lower, 1), '상한': round(upper, 1),
                             '이상치수': n_out, '이상치(%)': pct})

outlier_df = pd.DataFrame(outlier_summary).sort_values('이상치수', ascending=False)
print(outlier_df.to_string(index=False))

print("\n" + "="*60)
print("✅ EDA 1단계 완료! 결과 이미지가 output/eda/ 폴더에 저장되었습니다.")
print("="*60)
