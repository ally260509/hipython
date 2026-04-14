"use client"

import { useState } from "react"
import CarInputScreen from "@/components/car-input-screen"
import ConfirmationScreen from "@/components/confirmation-screen"
import ResultScreen from "@/components/result-screen"

export default function Home() {
  const [step, setStep] = useState(1)
  const [carData, setCarData] = useState<any>({})
  const [predictResult, setPredictResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleAnalyze = async () => {
    setLoading(true)
    try {
      const payload = {
        제조사: carData.manufacturer,
        모델: carData.model,
        연식: carData.year,
        주행거리: carData.mileage,
        배기량: parseInt(carData.displacement) || 1600,
        좌석수: carData.seats,
        연료: carData.fuel,
        변속기: carData.transmission === "자동" ? "자동" : "수동",
        색상: carData.color === "white" ? "흰색" : carData.color === "black" ? "검정색" : carData.color === "silver" ? "은색" : "기타",
        차급: carData.vehicleType,
        옵션: carData.options || [],
        사고여부: carData.hasAccident,
        교환개수: carData.exchangeCount,
        판금개수: carData.panelCount,
        보험이력건수: carData.insuranceCount,
        부식여부: carData.hasCorrosion,
      }

      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
      const result = await res.json()
      setPredictResult(result)
      setStep(3)
    } catch (e) {
      alert("예측 중 오류가 발생했습니다. Python 서버가 실행 중인지 확인해주세요.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {step === 1 && (
        <CarInputScreen
          onNext={(data: any) => {
            setCarData(data)
            setStep(2)
          }}
        />
      )}
      {step === 2 && (
        <ConfirmationScreen
          carData={carData}
          onBack={() => setStep(1)}
          onNext={handleAnalyze}
          loading={loading}
        />
      )}
      {step === 3 && (
        <ResultScreen
          carData={carData}
          predictResult={predictResult}
          onReset={() => setStep(1)}
        />
      )}
    </>
  )
}
