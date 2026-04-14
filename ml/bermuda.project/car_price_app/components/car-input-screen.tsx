"use client"

import { useState } from "react"
import { ArrowLeft, ChevronRight, Check, Minus, Plus, X } from "lucide-react"
import { CAR_DATA, MANUFACTURERS } from "@/lib/car-data"

// 바텀시트 선택 모달
function BottomSheet({ title, options, onSelect, onClose }: {
  title: string
  options: string[]
  onSelect: (v: string) => void
  onClose: () => void
}) {
  return (
    <div className="absolute inset-0 z-50 flex flex-col justify-end bg-black/40 rounded-[40px]">
      <div className="bg-white rounded-t-2xl max-h-[70%] flex flex-col">
        <div className="flex items-center justify-between px-4 py-4 border-b border-[#F0F0F0]">
          <span className="font-bold text-[#1a1a1a]">{title}</span>
          <button onClick={onClose}><X className="w-5 h-5 text-[#999999]" /></button>
        </div>
        <div className="overflow-y-auto">
          {options.map((opt) => (
            <button
              key={opt}
              onClick={() => { onSelect(opt); onClose() }}
              className="w-full text-left px-4 py-3.5 text-sm text-[#1a1a1a] border-b border-[#F7F7F7] active:bg-[#FFF4EE]"
            >
              {opt}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

// Section Header Component
function SectionHeader({ title }: { title: string }) {
  return (
    <div className="flex items-center gap-2 mb-4">
      <div className="w-1 h-5 bg-[#FF7E36] rounded-full" />
      <h2 className="text-base font-semibold text-[#1a1a1a]">{title}</h2>
    </div>
  )
}

// Dropdown Button Component
function DropdownButton({
  label,
  placeholder,
  value,
  disabled = false,
  onClick,
}: {
  label: string
  placeholder: string
  value?: string
  disabled?: boolean
  onClick?: () => void
}) {
  return (
    <div className="mb-3">
      <label className="text-sm text-[#666666] mb-1.5 block">{label}</label>
      <button
        disabled={disabled}
        onClick={onClick}
        className={`w-full flex items-center justify-between px-4 py-3 rounded-lg text-left transition-colors ${
          disabled
            ? "bg-[#EEEEEE] text-[#AAAAAA] cursor-not-allowed"
            : "bg-[#F7F7F7] text-[#1a1a1a] active:bg-[#EEEEEE]"
        }`}
      >
        <span className={value ? "text-[#1a1a1a]" : "text-[#999999]"}>
          {value || placeholder}
        </span>
        <ChevronRight className="w-5 h-5 text-[#999999]" />
      </button>
    </div>
  )
}

// Chip Button Component
function ChipButton({ 
  label, 
  selected, 
  onClick 
}: { 
  label: string
  selected: boolean
  onClick: () => void 
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
        selected 
          ? "bg-[#FF7E36] text-white" 
          : "bg-[#F7F7F7] text-[#666666] active:bg-[#EEEEEE]"
      }`}
    >
      {label}
    </button>
  )
}

// Toggle Button Component
function ToggleButton({ 
  label, 
  selected, 
  onClick 
}: { 
  label: string
  selected: boolean
  onClick: () => void 
}) {
  return (
    <button
      onClick={onClick}
      className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-colors ${
        selected 
          ? "bg-[#FF7E36] text-white" 
          : "bg-[#F7F7F7] text-[#666666] border border-[#E5E5E5] active:bg-[#EEEEEE]"
      }`}
    >
      {label}
    </button>
  )
}

// Color Circle Component
function ColorCircle({ 
  color, 
  selected, 
  onClick 
}: { 
  color: string
  selected: boolean
  onClick: () => void 
}) {
  const bgColors: Record<string, string> = {
    white: "bg-white border-2 border-[#E5E5E5]",
    black: "bg-[#1a1a1a]",
    silver: "bg-[#C0C0C0]",
  }

  return (
    <button
      onClick={onClick}
      className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${bgColors[color]} ${
        selected ? "ring-2 ring-[#FF7E36] ring-offset-2" : ""
      }`}
    >
      {selected && (
        <Check className={`w-5 h-5 ${color === "white" ? "text-[#FF7E36]" : "text-white"}`} />
      )}
    </button>
  )
}

// Option Card Component
function OptionCard({ 
  icon, 
  label, 
  selected, 
  onClick 
}: { 
  icon: string
  label: string
  selected: boolean
  onClick: () => void 
}) {
  return (
    <button
      onClick={onClick}
      className={`flex flex-col items-center justify-center p-3 rounded-xl transition-colors aspect-square ${
        selected 
          ? "bg-[#FF7E36] text-white" 
          : "bg-[#F7F7F7] text-[#666666] active:bg-[#EEEEEE]"
      }`}
    >
      <span className="text-2xl mb-1">{icon}</span>
      <span className="text-xs font-medium text-center leading-tight">{label}</span>
    </button>
  )
}

// Stepper Component
function Stepper({ 
  label, 
  value, 
  onChange 
}: { 
  label: string
  value: number
  onChange: (value: number) => void 
}) {
  return (
    <div className="flex items-center justify-between mb-3">
      <label className="text-sm text-[#666666]">{label}</label>
      <div className="flex items-center gap-3 border border-[#E5E5E5] rounded-lg">
        <button 
          onClick={() => onChange(Math.max(0, value - 1))}
          className="w-10 h-10 flex items-center justify-center text-[#999999] active:bg-[#F7F7F7] rounded-l-lg"
        >
          <Minus className="w-4 h-4" />
        </button>
        <span className="w-8 text-center font-medium text-[#1a1a1a]">{value}</span>
        <button 
          onClick={() => onChange(value + 1)}
          className="w-10 h-10 flex items-center justify-center text-[#999999] active:bg-[#F7F7F7] rounded-r-lg"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

// Year Picker Component
function YearPicker({ 
  selectedYear, 
  onChange 
}: { 
  selectedYear: number
  onChange: (year: number) => void 
}) {
  const years = [2019, 2020, 2021, 2022, 2023, 2024]
  
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 -mx-1 px-1">
      {years.map((year) => (
        <button
          key={year}
          onClick={() => onChange(year)}
          className={`flex-shrink-0 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            selectedYear === year 
              ? "bg-[#FF7E36] text-white" 
              : "bg-[#F7F7F7] text-[#666666]"
          }`}
        >
          {year}
        </button>
      ))}
    </div>
  )
}

export default function CarInputScreen({ onNext }: { onNext?: (data: any) => void }) {
  // 바텀시트 상태
  const [sheet, setSheet] = useState<null | "제조사" | "모델" | "트림" | "배기량">(null)

  // State for all form inputs
  const [manufacturer, setManufacturer] = useState("")
  const [model, setModel] = useState("")
  const [trim, setTrim] = useState("")
  const [year, setYear] = useState(2021)
  const [mileage, setMileage] = useState(52000)
  const [displacement, setDisplacement] = useState("")
  const [seats, setSeats] = useState(5)
  const [vehicleType, setVehicleType] = useState("세단")
  const [fuel, setFuel] = useState("가솔린")
  const [transmission, setTransmission] = useState("자동")
  const [color, setColor] = useState("white")
  const [options, setOptions] = useState<string[]>(["헤드램프", "후방카메라", "스마트키", "네비게이션"])
  const [hasAccident, setHasAccident] = useState(false)
  const [exchangeCount, setExchangeCount] = useState(1)
  const [panelCount, setPanelCount] = useState(0)
  const [insuranceCount, setInsuranceCount] = useState(0)
  const [hasCorrosion, setHasCorrosion] = useState(false)

  const toggleOption = (option: string) => {
    setOptions(prev => 
      prev.includes(option) 
        ? prev.filter(o => o !== option) 
        : [...prev, option]
    )
  }

  const optionsList = [
    { icon: "💡", label: "헤드램프" },
    { icon: "🅿️", label: "주차감지" },
    { icon: "☀️", label: "선루프" },
    { icon: "📷", label: "후방카메라" },
    { icon: "❄️", label: "자동에어컨" },
    { icon: "🔑", label: "스마트키" },
    { icon: "🧭", label: "네비게이션" },
    { icon: "🔥", label: "열선시트" },
    { icon: "💨", label: "통풍시트" },
    { icon: "🪑", label: "가죽시트" },
  ]

  return (
    <div className="min-h-screen bg-[#f5f5f5] flex items-center justify-center p-4">
      {/* iPhone 14 Frame */}
      <div className="relative w-[375px] h-[812px] bg-black rounded-[50px] p-3 shadow-2xl">
        {/* Dynamic Island */}
        <div className="absolute top-4 left-1/2 -translate-x-1/2 w-[126px] h-[37px] bg-black rounded-full z-20" />
        
        {/* Screen */}
        <div className="relative w-full h-full bg-white rounded-[40px] overflow-hidden">
          {/* 바텀시트 */}
          {sheet === "제조사" && (
            <BottomSheet
              title="제조사 선택"
              options={MANUFACTURERS}
              onSelect={(v) => { setManufacturer(v); setModel(""); setTrim("") }}
              onClose={() => setSheet(null)}
            />
          )}
          {sheet === "모델" && manufacturer && (
            <BottomSheet
              title="모델 선택"
              options={CAR_DATA[manufacturer] ?? []}
              onSelect={(v) => { setModel(v); setTrim("") }}
              onClose={() => setSheet(null)}
            />
          )}
          {sheet === "트림" && (
            <BottomSheet
              title="세부 트림 선택"
              options={["기본", "스마트", "프리미엄", "인스퍼레이션", "익스클루시브", "모던", "럭셔리"]}
              onSelect={(v) => setTrim(v)}
              onClose={() => setSheet(null)}
            />
          )}
          {sheet === "배기량" && (
            <BottomSheet
              title="배기량 선택"
              options={["999", "1000", "1200", "1400", "1500", "1600", "1800", "2000", "2200", "2400", "2500", "2700", "3000", "3300", "3500", "3800", "4000", "4700", "5000"]}
              onSelect={(v) => setDisplacement(v)}
              onClose={() => setSheet(null)}
            />
          )}
          {/* Status Bar */}
          <div className="h-12 bg-white flex items-end justify-between px-8 pb-1 pt-2">
            <span className="text-xs font-semibold text-[#1a1a1a]">9:41</span>
            <div className="flex items-center gap-1">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2 17h2v4H2v-4zm4-5h2v9H6v-9zm4-4h2v13h-2V8zm4-3h2v16h-2V5zm4-2h2v18h-2V3z"/>
              </svg>
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z"/>
              </svg>
              <div className="flex items-center">
                <div className="w-6 h-3 border border-[#1a1a1a] rounded-sm relative">
                  <div className="absolute inset-0.5 bg-[#1a1a1a] rounded-sm" style={{ width: "80%" }} />
                </div>
              </div>
            </div>
          </div>

          {/* Header */}
          <div className="bg-white px-4 py-3 flex items-center justify-between border-b border-[#F0F0F0]">
            <button className="w-10 h-10 flex items-center justify-center -ml-2">
              <ArrowLeft className="w-6 h-6 text-[#1a1a1a]" />
            </button>
            <h1 className="text-lg font-bold text-[#1a1a1a]">내 차 팔기</h1>
            <div className="flex items-center gap-1.5 mr-1">
              <div className="w-2 h-2 rounded-full bg-[#FF7E36]" />
              <div className="w-2 h-2 rounded-full bg-[#E5E5E5]" />
              <div className="w-2 h-2 rounded-full bg-[#E5E5E5]" />
            </div>
          </div>

          {/* Progress Bar */}
          <div className="h-1 bg-[#F0F0F0]">
            <div className="h-full bg-[#FF7E36] transition-all duration-300" style={{ width: "33%" }} />
          </div>

          {/* Scrollable Content */}
          <div className="overflow-y-auto h-[calc(100%-180px)] pb-4">
            {/* Section A: Vehicle Basic Info */}
            <div className="px-4 pt-5">
              <SectionHeader title="차량 기본 정보" />
              <DropdownButton
                label="제조사"
                placeholder="제조사 선택"
                value={manufacturer}
                onClick={() => setSheet("제조사")}
              />
              <DropdownButton
                label="모델"
                placeholder="모델 선택"
                value={model}
                disabled={!manufacturer}
                onClick={() => setSheet("모델")}
              />
              <DropdownButton
                label="세부 트림"
                placeholder="트림 선택"
                value={trim}
                disabled={!model}
                onClick={() => setSheet("트림")}
              />
            </div>

            {/* Section B: Vehicle Details */}
            <div className="px-4 pt-5 border-t border-[#F0F0F0] mt-4">
              <SectionHeader title="차량 상세 정보" />
              
              <label className="text-sm text-[#666666] mb-2 block">연식</label>
              <YearPicker selectedYear={year} onChange={setYear} />

              <label className="text-sm text-[#666666] mb-2 mt-4 block">주행거리</label>
              <div className="mb-4">
                <input 
                  type="range" 
                  min="0" 
                  max="300000" 
                  value={mileage}
                  onChange={(e) => setMileage(Number(e.target.value))}
                  className="w-full h-2 bg-[#F0F0F0] rounded-lg appearance-none cursor-pointer accent-[#FF7E36]"
                />
                <div className="flex justify-between mt-1">
                  <span className="text-xs text-[#999999]">0km</span>
                  <span className="text-sm font-semibold text-[#FF7E36]">{mileage.toLocaleString()} km</span>
                  <span className="text-xs text-[#999999]">30만km</span>
                </div>
              </div>

              <DropdownButton
                label="배기량 (cc)"
                placeholder="배기량 선택"
                value={displacement ? `${displacement}cc` : ""}
                onClick={() => setSheet("배기량")}
              />

              <label className="text-sm text-[#666666] mb-2 block">좌석수</label>
              <div className="flex gap-2 mb-3">
                {[5, 7, 9].map((num) => (
                  <ChipButton 
                    key={num}
                    label={`${num}인승`}
                    selected={seats === num}
                    onClick={() => setSeats(num)}
                  />
                ))}
              </div>
            </div>

            {/* Section C: Vehicle Type */}
            <div className="px-4 pt-5 border-t border-[#F0F0F0] mt-4">
              <SectionHeader title="차량 유형" />
              
              <label className="text-sm text-[#666666] mb-2 block">차급</label>
              <div className="flex gap-2 mb-4">
                <ToggleButton 
                  label="SUV" 
                  selected={vehicleType === "SUV"}
                  onClick={() => setVehicleType("SUV")}
                />
                <ToggleButton 
                  label="세단" 
                  selected={vehicleType === "세단"}
                  onClick={() => setVehicleType("세단")}
                />
              </div>

              <label className="text-sm text-[#666666] mb-2 block">연료</label>
              <div className="grid grid-cols-3 gap-2 mb-4">
                {["가솔린", "디젤", "LPG", "하이브리드", "수소", "기타"].map((f) => (
                  <ChipButton 
                    key={f}
                    label={f}
                    selected={fuel === f}
                    onClick={() => setFuel(f)}
                  />
                ))}
              </div>

              <label className="text-sm text-[#666666] mb-2 block">변속기</label>
              <div className="flex gap-2 mb-4">
                <ToggleButton 
                  label="자동" 
                  selected={transmission === "자동"}
                  onClick={() => setTransmission("자동")}
                />
                <ToggleButton 
                  label="수동" 
                  selected={transmission === "수동"}
                  onClick={() => setTransmission("수동")}
                />
              </div>

              <label className="text-sm text-[#666666] mb-2 block">색상</label>
              <div className="flex items-center gap-3 mb-3">
                <ColorCircle 
                  color="white" 
                  selected={color === "white"}
                  onClick={() => setColor("white")}
                />
                <ColorCircle 
                  color="black" 
                  selected={color === "black"}
                  onClick={() => setColor("black")}
                />
                <ColorCircle 
                  color="silver" 
                  selected={color === "silver"}
                  onClick={() => setColor("silver")}
                />
                <ChipButton 
                  label="기타" 
                  selected={color === "other"}
                  onClick={() => setColor("other")}
                />
              </div>
            </div>

            {/* Section D: Options */}
            <div className="px-4 pt-5 border-t border-[#F0F0F0] mt-4">
              <SectionHeader title="옵션" />
              <div className="grid grid-cols-3 gap-2">
                {optionsList.map((opt) => (
                  <OptionCard 
                    key={opt.label}
                    icon={opt.icon}
                    label={opt.label}
                    selected={options.includes(opt.label)}
                    onClick={() => toggleOption(opt.label)}
                  />
                ))}
              </div>
            </div>

            {/* Section E: Accident History */}
            <div className="px-4 pt-5 border-t border-[#F0F0F0] mt-4 pb-6">
              <SectionHeader title="사고/이력" />
              
              <label className="text-sm text-[#666666] mb-2 block">사고 여부</label>
              <div className="flex gap-2 mb-4">
                <ToggleButton 
                  label="있음" 
                  selected={hasAccident}
                  onClick={() => setHasAccident(true)}
                />
                <ToggleButton 
                  label="없음" 
                  selected={!hasAccident}
                  onClick={() => setHasAccident(false)}
                />
              </div>

              <Stepper 
                label="교환 개수" 
                value={exchangeCount}
                onChange={setExchangeCount}
              />
              <Stepper 
                label="판금 개수" 
                value={panelCount}
                onChange={setPanelCount}
              />
              <Stepper 
                label="보험이력 건수" 
                value={insuranceCount}
                onChange={setInsuranceCount}
              />

              <label className="text-sm text-[#666666] mb-2 block mt-1">부식 여부</label>
              <div className="flex gap-2">
                <ToggleButton 
                  label="있음" 
                  selected={hasCorrosion}
                  onClick={() => setHasCorrosion(true)}
                />
                <ToggleButton 
                  label="없음" 
                  selected={!hasCorrosion}
                  onClick={() => setHasCorrosion(false)}
                />
              </div>
            </div>
          </div>

          {/* Fixed Bottom CTA */}
          <div className="absolute bottom-0 left-0 right-0 bg-white border-t border-[#F0F0F0] px-4 pt-2 pb-8">
            <p className="text-xs text-[#999999] text-center mb-2">필수 항목을 모두 입력해주세요</p>
            <button
              onClick={() => onNext?.({ manufacturer, model, trim, year, mileage, displacement, seats, vehicleType, fuel, transmission, color, options, hasAccident, exchangeCount, panelCount, insuranceCount, hasCorrosion })}
              className="w-full h-[52px] bg-[#FF7E36] text-white font-semibold rounded-xl flex items-center justify-center gap-2 active:bg-[#E56A2A] transition-colors">
              다음 단계로
              <span className="text-lg">→</span>
            </button>
          </div>

          {/* Home Indicator */}
          <div className="absolute bottom-1 left-1/2 -translate-x-1/2 w-32 h-1 bg-black/20 rounded-full" />
        </div>
      </div>
    </div>
  )
}
