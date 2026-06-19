"use client";

import { useState } from "react";

function apiBaseUrl() {
  if (typeof window === "undefined") {
    return "";
  }

  if (window.location.port === "3000") {
    return `${window.location.protocol}//${window.location.hostname}:4000`;
  }

  return "";
}

export function AttendancePanel() {
  const [status, setStatus] = useState("오늘 근태를 기록해 주세요.");

  async function clock(type: "clock-in" | "clock-out") {
    const response = await fetch(`${apiBaseUrl()}/api/attendance/${type}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ memo: "웹 대시보드 기록" })
    });

    setStatus(response.ok ? `${type === "clock-in" ? "출근" : "퇴근"} 기록이 저장되었습니다.` : "근태 기록 저장에 실패했습니다.");
  }

  return (
    <section className="panel">
      <div className="section-heading">
        <p>근태</p>
        <span>출퇴근 API, 연차 잔여, 캘린더 UI</span>
      </div>
      <div className="attendance-actions">
        <button onClick={() => clock("clock-in")}>출근 기록</button>
        <button className="secondary" onClick={() => clock("clock-out")}>퇴근 기록</button>
      </div>
      <p className="status">{status}</p>
      <div className="calendar">
        {["월", "화", "수", "목", "금"].map((day, index) => (
          <div key={day}>
            <strong>{day}</strong>
            <span>{index === 2 ? "연차 7.5일 잔여" : "정상 근무"}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
