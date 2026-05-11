import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import App from "../App.jsx";

// Mock the entire api module so no real fetch calls are made.
// authStore.jsx imports { api } from "../api.js" — same module resolved here.
vi.mock("../api.js", () => ({
  api: {
    me: vi.fn().mockRejectedValue(new Error("no token")),
    login: vi.fn(),
    signup: vi.fn(),
    listBabies: vi.fn().mockResolvedValue([]),
    refMilestones: vi.fn().mockResolvedValue([]),
    refVaccines: vi.fn().mockResolvedValue([]),
    refFeeding: vi.fn().mockResolvedValue([]),
    refGrowthCurves: vi.fn().mockResolvedValue([]),
    refGrowthTable: vi.fn().mockResolvedValue([]),
  },
}));

beforeEach(() => {
  localStorage.clear();
});

describe("App", () => {
  it("renders without crashing", () => {
    const { container } = render(<App />);
    expect(container.firstChild).toBeTruthy();
  });

  it("shows auth page when no token is present", () => {
    // React 18 act() flushes effects before assertions, so after render()
    // the auth loading is already resolved and AuthPage is displayed.
    const { container } = render(<App />);
    expect(container.querySelector(".auth-page")).toBeInTheDocument();
  });

  it("shows email and password inputs for login", () => {
    const { container } = render(<App />);
    expect(container.querySelector("input[type='email']")).toBeInTheDocument();
    expect(container.querySelector("input[type='password']")).toBeInTheDocument();
  });
});
