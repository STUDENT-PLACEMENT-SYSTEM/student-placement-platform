"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { LiveKPIData, LivePlacementEvent } from "../lib/types";
import { MOCK_KPI_DATA, tokenManager } from "../lib/api";

const SSE_URL =
  process.env.NEXT_PUBLIC_SSE_URL ||
  "http://localhost:8000/api/v1/analytics/live-kpis";

const INITIAL_EVENTS: LivePlacementEvent[] = [
  {
    id: "evt-01",
    timestamp: new Date(Date.now() - 1000 * 60 * 3).toISOString(),
    student_name: "Rohan Sharma",
    roll_number: "2021CS045",
    branch: "Computer Science",
    company: "Amazon AWS",
    ctc_lpa: 24.5,
    type: "offer",
    message: "Accepted SDE-1 offer at Amazon AWS (₹24.50 LPA)",
  },
  {
    id: "evt-02",
    timestamp: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
    student_name: "Ananya Iyer",
    roll_number: "2021CS089",
    branch: "Computer Science",
    company: "Oracle Cloud",
    ctc_lpa: 19.0,
    type: "offer",
    message: "Accepted MTS Full-Stack offer at Oracle (₹19.00 LPA)",
  },
  {
    id: "evt-03",
    timestamp: new Date(Date.now() - 1000 * 60 * 25).toISOString(),
    student_name: "Aditya Verma",
    roll_number: "2021IT024",
    branch: "Information Technology",
    company: "Cisco Systems",
    ctc_lpa: 15.0,
    type: "offer",
    message: "Placed as Platform Engineer at Cisco Systems (₹15.00 LPA)",
  },
  {
    id: "evt-04",
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    student_name: "Sarah Jenkins",
    company: "Amazon AWS",
    type: "drive_announced",
    message: "Announced SDE-1 Campus Drive (Registration deadline Dec 3)",
  },
];

const SIMULATED_COMPANIES = [
  { name: "Google", ctc: 36.0, branch: "Computer Science" },
  { name: "Microsoft", ctc: 28.5, branch: "Information Technology" },
  { name: "Amazon AWS", ctc: 24.5, branch: "Computer Science" },
  { name: "Oracle Cloud", ctc: 19.0, branch: "ECE" },
  { name: "DE Shaw & Co", ctc: 48.0, branch: "Computer Science" },
  { name: "Goldman Sachs", ctc: 26.0, branch: "Information Technology" },
  { name: "Cisco Systems", ctc: 15.0, branch: "ECE" },
];

const SIMULATED_STUDENTS = [
  { name: "Kunal Singhal", roll: "2021CS052" },
  { name: "Divya Nair", roll: "2021EC089" },
  { name: "Siddharth Rao", roll: "2021CS118" },
  { name: "Pooja Hegde", roll: "2021IT074" },
  { name: "Varun Mehta", roll: "2021CS143" },
  { name: "Meera Krishnan", roll: "2021EC078" },
];

export function useSSE() {
  const [data, setData] = useState<LiveKPIData>(MOCK_KPI_DATA);
  const [events, setEvents] = useState<LivePlacementEvent[]>(INITIAL_EVENTS);
  const [latestEvent, setLatestEvent] = useState<LivePlacementEvent | null>(
    INITIAL_EVENTS[0]
  );
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isSimulated, setIsSimulated] = useState<boolean>(false);
  const [lastHeartbeat, setLastHeartbeat] = useState<Date>(new Date());
  const eventSourceRef = useRef<EventSource | null>(null);

  // Manual Trigger to simulate an offer live (e.g. from Mark Placed modal)
  const injectPlacementEvent = useCallback(
    (studentName: string, company: string, ctc: number, branch = "Computer Science") => {
      const newEvent: LivePlacementEvent = {
        id: `evt-${Date.now()}`,
        timestamp: new Date().toISOString(),
        student_name: studentName,
        company,
        ctc_lpa: ctc,
        branch,
        type: "offer",
        message: `Accepted offer at ${company} (₹${ctc.toFixed(2)} LPA)`,
      };

      setLatestEvent(newEvent);
      setEvents((prev) => [newEvent, ...prev.slice(0, 25)]);

      setData((prev) => {
        const newPlaced = prev.placed_students + 1;
        const newTotalOffers = prev.total_offers + 1;
        const newPercent = (newPlaced / prev.total_students) * 100;
        const newAvg = Number(
          (
            (prev.average_ctc_lpa * prev.placed_students + ctc) /
            newPlaced
          ).toFixed(2)
        );
        const newHighest = Math.max(prev.highest_ctc_lpa, ctc);

        const currentBranch = prev.branch_breakdown[branch] || {
          placed: 0,
          total: 100,
          percent: 0,
        };
        const branchPlaced = currentBranch.placed + 1;

        return {
          ...prev,
          timestamp: new Date().toISOString(),
          placed_students: newPlaced,
          placement_percentage: Number(newPercent.toFixed(2)),
          total_offers: newTotalOffers,
          average_ctc_lpa: newAvg,
          highest_ctc_lpa: newHighest,
          branch_breakdown: {
            ...prev.branch_breakdown,
            [branch]: {
              ...currentBranch,
              placed: branchPlaced,
              percent: Number(
                ((branchPlaced / currentBranch.total) * 100).toFixed(1)
              ),
            },
          },
          recent_offer: {
            student_name: studentName,
            company,
            ctc_lpa: ctc,
          },
        };
      });
    },
    []
  );

  useEffect(() => {
    let mockInterval: NodeJS.Timeout | null = null;
    let sse: EventSource | null = null;

    try {
      // Connect to SSE if browser environment
      if (typeof window !== "undefined") {
        const token = tokenManager.getAccessToken();
        const urlWithAuth = token
          ? `${SSE_URL}?token=${encodeURIComponent(token)}`
          : SSE_URL;

        sse = new EventSource(urlWithAuth);
        eventSourceRef.current = sse;

        sse.onopen = () => {
          setIsConnected(true);
          setIsSimulated(false);
          setLastHeartbeat(new Date());
        };

        // Listen for standard message / kpi_update
        sse.addEventListener("kpi_update", (e: MessageEvent) => {
          try {
            const parsed = JSON.parse(e.data) as LiveKPIData;
            setData(parsed);
            setLastHeartbeat(new Date());
            if (parsed.recent_offer) {
              const offerEvent: LivePlacementEvent = {
                id: `evt-${Date.now()}`,
                timestamp: new Date().toISOString(),
                student_name: parsed.recent_offer.student_name,
                company: parsed.recent_offer.company,
                ctc_lpa: parsed.recent_offer.ctc_lpa,
                type: "offer",
                message: `Placed at ${parsed.recent_offer.company} for ₹${parsed.recent_offer.ctc_lpa} LPA`,
              };
              setLatestEvent(offerEvent);
              setEvents((prev) => [offerEvent, ...prev.slice(0, 25)]);
            }
          } catch (err) {
            console.error("Error parsing SSE event:", err);
          }
        });

        sse.addEventListener("placement_event", (e: MessageEvent) => {
          try {
            const ev = JSON.parse(e.data) as LivePlacementEvent;
            setLatestEvent(ev);
            setEvents((prev) => [ev, ...prev.slice(0, 25)]);
            setLastHeartbeat(new Date());
          } catch (err) {
            console.error("Error parsing placement event:", err);
          }
        });

        sse.onerror = () => {
          // Fall back gracefully to live simulation mode when API server is not running SSE
          sse?.close();
          setIsConnected(true);
          setIsSimulated(true);
        };
      }
    } catch {
      setIsConnected(true);
      setIsSimulated(true);
    }

    // Realistic background tick simulation every 14 seconds when simulated
    mockInterval = setInterval(() => {
      setLastHeartbeat(new Date());
      // 40% chance of a new placement event popping up
      if (Math.random() > 0.45) {
        const randomComp =
          SIMULATED_COMPANIES[
            Math.floor(Math.random() * SIMULATED_COMPANIES.length)
          ];
        const randomStu =
          SIMULATED_STUDENTS[
            Math.floor(Math.random() * SIMULATED_STUDENTS.length)
          ];
        injectPlacementEvent(
          randomStu.name,
          randomComp.name,
          randomComp.ctc,
          randomComp.branch
        );
      }
    }, 14000);

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (mockInterval) {
        clearInterval(mockInterval);
      }
    };
  }, [injectPlacementEvent]);

  return {
    data,
    events,
    latestEvent,
    isConnected,
    isSimulated,
    lastHeartbeat,
    injectPlacementEvent,
  };
}
