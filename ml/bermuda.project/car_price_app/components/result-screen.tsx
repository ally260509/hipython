"use client"

import { ArrowLeft, Zap, Check, Coins, TrendingUp, TrendingDown } from "lucide-react"

export default function ResultScreen({ carData, predictResult, onReset }: { carData?: any, predictResult?: any, onReset?: () => void }) {
  const fmt = (v: number) => `${Math.round(v).toLocaleString()}만원`

  const mid   = predictResult?.적정판매_가격   ?? 0
  const low   = predictResult?.빠른판매_가격   ?? 0
  const high  = predictResult?.최대수익_가격   ?? 0
  const sMin  = predictResult?.유사차량_최저가 ?? 0
  const sAvg  = predictResult?.유사차량_평균가 ?? 0
  const sMax  = predictResult?.유사차량_최고가 ?? 0

  // 내 차 위치 % (최저~최고 사이)
  const markerPct = sMax > sMin ? Math.round(((mid - sMin) / (sMax - sMin)) * 100) : 50

  const colorLabel: Record<string, string> = { white: "흰색", black: "검정색", silver: "은색", other: "기타" }

  // 가격 분석 요인 동적 생성
  const priceFactors: { label: string; impact: number }[] = []

  // 주행거리
  const mileage = carData?.mileage ?? 0
  if (mileage < 30000)       priceFactors.push({ label: "낮은 주행거리", impact: 60 })
  else if (mileage < 70000)  priceFactors.push({ label: "적정 주행거리", impact: 20 })
  else if (mileage > 150000) priceFactors.push({ label: "높은 주행거리", impact: -80 })
  else if (mileage > 100000) priceFactors.push({ label: "높은 주행거리", impact: -40 })

  // 옵션
  const optionImpact: Record<string, number> = {
    "선루프": 20, "가죽시트": 20, "통풍시트": 15,
    "후방카메라": 15, "헤드램프": 10, "스마트키": 10,
    "열선시트": 8, "네비게이션": 8, "자동에어컨": 5, "주차감지": 5,
  }
  for (const opt of (carData?.options ?? [])) {
    if (optionImpact[opt]) priceFactors.push({ label: opt, impact: optionImpact[opt] })
  }

  // 색상
  if (carData?.color === "black") priceFactors.push({ label: "검정색 (인기 색상)", impact: 5 })
  if (carData?.color === "other") priceFactors.push({ label: "기타 색상 (수요 낮음)", impact: -5 })
  if (carData?.color === "white") priceFactors.push({ label: "흰색 (수요 보통)", impact: -3 })

  // 사고/이력
  if (carData?.hasAccident)                         priceFactors.push({ label: "사고 이력", impact: -100 })
  if ((carData?.exchangeCount ?? 0) > 0)            priceFactors.push({ label: `교환 ${carData.exchangeCount}개`, impact: -(carData.exchangeCount * 30) })
  if ((carData?.panelCount ?? 0) > 0)               priceFactors.push({ label: `판금 ${carData.panelCount}개`, impact: -(carData.panelCount * 15) })
  if ((carData?.insuranceCount ?? 0) > 0)           priceFactors.push({ label: `보험이력 ${carData.insuranceCount}건`, impact: -(carData.insuranceCount * 10) })
  if (carData?.hasCorrosion)                         priceFactors.push({ label: "부식", impact: -20 })

  const positiveFactors = priceFactors.filter(f => f.impact > 0).sort((a, b) => b.impact - a.impact)
  const negativeFactors = priceFactors.filter(f => f.impact < 0).sort((a, b) => a.impact - b.impact)


  return (
    <div className="flex items-center justify-center min-h-screen bg-muted p-4">
      {/* iPhone 14 Frame */}
      <div className="relative w-[375px] h-[812px] bg-foreground rounded-[50px] p-3 shadow-2xl">
        {/* Screen */}
        <div className="relative w-full h-full bg-background rounded-[38px] overflow-hidden flex flex-col">
          {/* Dynamic Island */}
          <div className="absolute top-3 left-1/2 -translate-x-1/2 w-[120px] h-[34px] bg-foreground rounded-full z-10" />
          
          {/* Status Bar */}
          <div className="flex items-center justify-between px-8 pt-4 pb-2">
            <span className="text-xs font-medium">9:41</span>
            <div className="flex items-center gap-1">
              <div className="flex items-center gap-0.5">
                <div className="w-4 h-2 border border-foreground rounded-sm relative">
                  <div className="absolute inset-0.5 bg-foreground rounded-[1px]" style={{ width: "80%" }} />
                </div>
              </div>
            </div>
          </div>

          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 mt-4">
            <button className="p-2 -ml-2">
              <ArrowLeft className="w-5 h-5 text-foreground" />
            </button>
            <h1 className="text-lg font-bold text-foreground">가격 분석 결과</h1>
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full bg-primary" />
              <div className="w-2 h-2 rounded-full bg-primary" />
              <div className="w-2 h-2 rounded-full bg-primary" />
            </div>
          </div>

          {/* Progress Bar */}
          <div className="px-4 pb-3">
            <div className="h-1 bg-muted rounded-full overflow-hidden">
              <div className="h-full bg-primary rounded-full" style={{ width: "100%" }} />
            </div>
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto px-4 pb-32">
            {/* Vehicle Subtitle */}
            <p className="text-sm text-muted-foreground mb-4">
              {carData?.manufacturer} {carData?.model} · {carData?.year}년 · {(carData?.mileage / 10000).toFixed(1)}만km · {carData?.fuel}
            </p>

            {/* Hero Card - AI Recommended Price */}
            <div 
              className="rounded-xl p-5 mb-5"
              style={{ background: "linear-gradient(135deg, #FF7E36 0%, #FF9A5E 100%)" }}
            >
              <div className="flex items-center gap-1.5 mb-2">
                <span className="text-sm text-white/90">🎯 AI 추천 적정 판매가</span>
              </div>
              <p className="text-4xl font-bold text-white mb-3">{fmt(mid)}</p>
              <div className="flex items-center gap-3">
                <span className="inline-block bg-white text-primary text-xs font-medium px-3 py-1 rounded-full">
                  시세 대비 상위 42%
                </span>
              </div>
              <p className="text-xs text-white/80 mt-3">3,200개 유사 매물 분석 기준</p>
            </div>

            {/* Pricing Strategy Cards */}
            <div className="mb-5">
              <h2 className="text-base font-bold text-foreground mb-3">판매 전략별 가격</h2>
              <div className="grid grid-cols-3 gap-2">
                {/* Quick Sale */}
                <div className="bg-card rounded-xl p-3 text-center border border-border">
                  <div className="w-8 h-8 mx-auto mb-2 bg-blue-100 rounded-full flex items-center justify-center">
                    <Zap className="w-4 h-4 text-blue-500" />
                  </div>
                  <p className="text-xs text-muted-foreground mb-1">빠른 판매</p>
                  <p className="text-sm font-bold text-foreground mb-1">{fmt(low)}</p>
                  <p className="text-[10px] text-muted-foreground mb-2">평균 1주 이내</p>
                  <span className="inline-block bg-blue-100 text-blue-600 text-[10px] px-2 py-0.5 rounded-full">
                    빠른 거래
                  </span>
                </div>

                {/* Optimal Sale - Highlighted */}
                <div className="bg-card rounded-xl p-3 text-center border-2 border-primary relative">
                  <div className="w-8 h-8 mx-auto mb-2 bg-orange-100 rounded-full flex items-center justify-center">
                    <Check className="w-4 h-4 text-primary" />
                  </div>
                  <p className="text-xs text-muted-foreground mb-1">적정 판매</p>
                  <p className="text-sm font-bold text-primary mb-1">{fmt(mid)}</p>
                  <p className="text-[10px] text-muted-foreground mb-2">평균 2~3주</p>
                  <span className="inline-block bg-primary text-white text-[10px] px-2 py-0.5 rounded-full">
                    AI 추천
                  </span>
                </div>

                {/* Maximum Profit */}
                <div className="bg-card rounded-xl p-3 text-center border border-border">
                  <div className="w-8 h-8 mx-auto mb-2 bg-green-100 rounded-full flex items-center justify-center">
                    <Coins className="w-4 h-4 text-green-600" />
                  </div>
                  <p className="text-xs text-muted-foreground mb-1">최대 수익</p>
                  <p className="text-sm font-bold text-foreground mb-1">{fmt(high)}</p>
                  <p className="text-[10px] text-muted-foreground mb-2">시간 여유 필요</p>
                  <span className="inline-block bg-green-100 text-green-600 text-[10px] px-2 py-0.5 rounded-full">
                    수익 극대화
                  </span>
                </div>
              </div>
            </div>

            {/* Similar Vehicle Prices */}
            <div className="mb-5">
              <h2 className="text-base font-bold text-foreground mb-3">유사 차량 시세</h2>
              <div className="bg-card rounded-xl p-4">
                <div className="grid grid-cols-3 text-center mb-4">
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">최저가</p>
                    <p className="text-sm font-bold text-foreground">{Math.round(sMin)}만</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">평균가</p>
                    <p className="text-sm font-bold text-foreground">{Math.round(sAvg)}만</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">최고가</p>
                    <p className="text-sm font-bold text-foreground">{Math.round(sMax)}만</p>
                  </div>
                </div>
                
                {/* Range Bar */}
                <div className="relative h-2 bg-border rounded-full mb-2">
                  <div 
                    className="absolute h-full bg-primary rounded-full"
                    style={{ left: "0%", width: "100%" }}
                  />
                  {/* My Car Marker */}
                  <div 
                    className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2"
                    style={{ left: `${markerPct}%` }}
                  >
                    <div className="w-4 h-4 bg-primary rounded-full border-2 border-white shadow-md" />
                  </div>
                </div>
                <div className="text-center">
                  <span
                    className="inline-block text-[10px] text-primary font-medium"
                    style={{ marginLeft: `calc(${markerPct}% - 16px)` }}
                  >
                    내 차
                  </span>
                </div>
              </div>
            </div>

            {/* Price Analysis */}
            <div className="mb-5">
              <h2 className="text-base font-bold text-foreground mb-3">가격 분석</h2>
              <div className="bg-card rounded-xl p-4">
                <div className="mb-4">
                  <div className="flex items-center gap-1.5 mb-3">
                    <TrendingUp className="w-4 h-4 text-green-500" />
                    <span className="text-sm font-medium text-green-600">가격 상승 요인</span>
                  </div>
                  <div className="space-y-2">
                    {positiveFactors.length === 0 && <p className="text-sm text-muted-foreground">해당 없음</p>}
                    {positiveFactors.map((f) => (
                      <div key={f.label} className="flex items-center justify-between">
                        <span className="text-sm text-foreground">{f.label}</span>
                        <span className="text-sm font-medium text-green-500">+{f.impact}만원</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="h-px bg-border my-4" />

                <div>
                  <div className="flex items-center gap-1.5 mb-3">
                    <TrendingDown className="w-4 h-4 text-red-500" />
                    <span className="text-sm font-medium text-red-500">가격 하락 요인</span>
                  </div>
                  <div className="space-y-2">
                    {negativeFactors.length === 0 && <p className="text-sm text-muted-foreground">해당 없음</p>}
                    {negativeFactors.map((f) => (
                      <div key={f.label} className="flex items-center justify-between">
                        <span className="text-sm text-foreground">{f.label}</span>
                        <span className="text-sm font-medium text-red-500">{f.impact}만원</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Fixed Bottom CTA */}
          <div className="absolute bottom-0 left-0 right-0 bg-background border-t border-border px-4 pt-3 pb-8">
            <button className="w-full bg-primary text-white font-semibold py-4 rounded-xl text-base">
              당근마켓에 바로 올리기 🥕
            </button>
            <button onClick={onReset} className="w-full text-center text-sm text-muted-foreground mt-3">
              다시 입력하기
            </button>
          </div>

          {/* Home Indicator */}
          <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-32 h-1 bg-foreground/20 rounded-full" />
        </div>
      </div>
    </div>
  )
}
