"use client"

import { ArrowLeft, Check, Zap } from "lucide-react"

const ALL_OPTIONS = ["헤드램프", "주차감지", "선루프", "후방카메라", "자동에어컨", "스마트키", "네비게이션", "열선시트", "통풍시트", "가죽시트"]
const COLOR_LABEL: Record<string, string> = { white: "흰색", black: "검정색", silver: "은색", other: "기타" }

export default function ConfirmationScreen({ carData, onBack, onNext, loading }: { carData?: any, onBack?: () => void, onNext?: () => void, loading?: boolean }) {
  const selectedOptions = (carData?.options ?? []) as string[]
  const unselectedOptions = ALL_OPTIONS.filter(o => !selectedOptions.includes(o))

  return (
    <div className="flex items-center justify-center min-h-screen bg-muted p-4">
      {/* iPhone 14 Frame */}
      <div className="relative w-[375px] h-[812px] bg-foreground rounded-[50px] p-3 shadow-2xl">
        {/* Screen */}
        <div className="relative w-full h-full bg-background rounded-[40px] overflow-hidden flex flex-col">
          {/* Dynamic Island */}
          <div className="absolute top-3 left-1/2 -translate-x-1/2 w-[126px] h-[37px] bg-foreground rounded-full z-10" />

          {/* Status Bar */}
          <div className="flex justify-between items-center px-8 pt-4 pb-2 text-foreground text-xs font-medium">
            <span>9:41</span>
            <div className="flex items-center gap-1">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2 17h2v4H2v-4zm4-5h2v9H6v-9zm4-4h2v13h-2V8zm4-3h2v16h-2V5zm4-2h2v18h-2V3z" />
              </svg>
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 3C7.5 3 3.75 5.44 2 9c1.75 3.56 5.5 6 10 6s8.25-2.44 10-6c-1.75-3.56-5.5-6-10-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z" />
              </svg>
              <div className="w-6 h-3 border border-current rounded-sm relative">
                <div className="absolute inset-[2px] right-1 bg-current rounded-sm" />
              </div>
            </div>
          </div>

          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-border">
            <button className="w-10 h-10 flex items-center justify-center" onClick={onBack}>
              <ArrowLeft className="w-6 h-6 text-foreground" />
            </button>
            <h1 className="text-lg font-bold text-foreground">입력 확인</h1>
            <div className="flex items-center gap-1.5 w-10 justify-end">
              <div className="w-2 h-2 rounded-full bg-primary" />
              <div className="w-2 h-2 rounded-full bg-primary" />
              <div className="w-2 h-2 rounded-full bg-border" />
            </div>
          </div>

          {/* Progress Bar */}
          <div className="h-1 bg-muted">
            <div className="h-full bg-primary transition-all duration-300" style={{ width: "66%" }} />
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-4 flex flex-col gap-4">
              {/* Vehicle Title Block */}
              <div className="flex items-center gap-4 py-2">
                <div className="flex-1">
                  <h2 className="text-xl font-bold text-foreground">{carData?.manufacturer} {carData?.model} {carData?.trim}</h2>
                  <p className="text-sm text-muted-foreground mt-1">{carData?.year}년식 · {((carData?.mileage ?? 0) / 10000).toFixed(1)}만km · {carData?.fuel}</p>
                </div>
                <div className="w-16 h-16 bg-muted rounded-xl flex items-center justify-center text-3xl">
                  🚗
                </div>
              </div>

              {/* Card 1: 기본 정보 */}
              <div className="bg-card rounded-xl p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold text-foreground">기본 정보</h3>
                  <button className="text-sm text-primary font-medium">수정</button>
                </div>
                <div className="flex flex-col gap-3">
                  <InfoRow label="연식" value={`${carData?.year}년`} />
                  <InfoRow label="주행거리" value={`${(carData?.mileage ?? 0).toLocaleString()} km`} />
                  <InfoRow label="배기량" value={`${carData?.displacement}`} />
                  <InfoRow label="연료" value={carData?.fuel ?? ""} />
                  <InfoRow label="변속기" value={carData?.transmission ?? ""} />
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">색상</span>
                    <span className="text-sm font-medium text-foreground">{COLOR_LABEL[carData?.color] ?? "기타"}</span>
                  </div>
                  <InfoRow label="차급" value={carData?.vehicleType ?? ""} />
                  <InfoRow label="좌석수" value={`${carData?.seats}인승`} />
                </div>
              </div>

              {/* Card 2: 선택 옵션 */}
              <div className="bg-card rounded-xl p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold text-foreground">선택 옵션</h3>
                  <button className="text-sm text-primary font-medium">수정</button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {selectedOptions.map((option) => (
                    <span
                      key={option}
                      className="px-3 py-1.5 bg-primary text-primary-foreground text-sm rounded-full font-medium"
                    >
                      {option}
                    </span>
                  ))}
                  {unselectedOptions.map((option) => (
                    <span
                      key={option}
                      className="px-3 py-1.5 bg-background text-muted-foreground text-sm rounded-full border border-border"
                    >
                      {option}
                    </span>
                  ))}
                </div>
              </div>

              {/* Card 3: 사고/이력 */}
              <div className="bg-card rounded-xl p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold text-foreground">사고/이력</h3>
                  <button className="text-sm text-primary font-medium">수정</button>
                </div>
                <div className="flex flex-col gap-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">사고 여부</span>
                    <div className="flex items-center gap-1.5">
                      <span className="text-sm font-medium text-foreground">{carData?.hasAccident ? "있음" : "없음"}</span>
                      {!carData?.hasAccident && <Check className="w-4 h-4 text-green-500" />}
                    </div>
                  </div>
                  <InfoRow label="교환" value={`${carData?.exchangeCount ?? 0}개`} />
                  <InfoRow label="판금" value={`${carData?.panelCount ?? 0}개`} />
                  <InfoRow label="보험이력" value={`${carData?.insuranceCount ?? 0}건`} />
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">부식</span>
                    <div className="flex items-center gap-1.5">
                      <span className="text-sm font-medium text-foreground">{carData?.hasCorrosion ? "있음" : "없음"}</span>
                      {!carData?.hasCorrosion && <Check className="w-4 h-4 text-green-500" />}
                    </div>
                  </div>
                </div>
              </div>

              {/* Info Banner */}
              <div className="bg-orange-50 rounded-xl p-4 flex items-center gap-3">
                <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <Zap className="w-4 h-4 text-primary" />
                </div>
                <p className="text-sm text-foreground leading-relaxed">
                  AI가 유사 차량 <span className="font-bold text-primary">3,200대</span>를 분석하여 최적 가격을 추천합니다
                </p>
              </div>
            </div>
          </div>

          {/* Fixed Bottom CTA */}
          <div className="p-4 border-t border-border bg-background">
            <button onClick={onNext} disabled={loading} className="w-full h-[52px] bg-primary text-primary-foreground font-bold text-base rounded-xl flex items-center justify-center gap-2 active:scale-[0.98] transition-transform disabled:opacity-60">
              {loading ? "AI 분석 중..." : "AI 가격 분석 시작하기"}
              {!loading && <span>→</span>}
            </button>
          </div>

          {/* Home Indicator */}
          <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-32 h-1 bg-foreground/20 rounded-full" />
        </div>
      </div>
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="text-sm font-medium text-foreground">{value}</span>
    </div>
  )
}
