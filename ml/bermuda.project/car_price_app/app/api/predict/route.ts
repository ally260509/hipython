import { NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  const carData = await request.json()

  const response = await fetch("http://localhost:8000/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(carData),
  })

  const result = await response.json()
  return NextResponse.json(result)
}
