'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isTokenValid } from '@/lib/auth';
import { FaRobot, FaChartLine, FaShieldAlt, FaBrain } from 'react-icons/fa';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    if (isTokenValid()) {
      router.push('/dashboard');
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-900">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold mb-6 gradient-text">
            Financial AI Platform
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Multi-Agent AI-Powered Financial Research & Portfolio Intelligence System
          </p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => router.push('/login')}
              className="px-8 py-3 bg-primary-600 hover:bg-primary-700 rounded-lg font-semibold transition"
            >
              Get Started
            </button>
            <button
              onClick={() => router.push('/signup')}
              className="px-8 py-3 bg-dark-700 hover:bg-dark-600 rounded-lg font-semibold transition"
            >
              Sign Up
            </button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mt-20">
          <FeatureCard
            icon={<FaRobot className="text-4xl text-primary-500" />}
            title="Multi-Agent AI"
            description="Multiple specialized AI agents working together to analyze your portfolio"
          />
          <FeatureCard
            icon={<FaChartLine className="text-4xl text-green-500" />}
            title="Real-time Analytics"
            description="Live market data and portfolio tracking with advanced analytics"
          />
          <FeatureCard
            icon={<FaShieldAlt className="text-4xl text-yellow-500" />}
            title="Risk Analysis"
            description="Comprehensive risk assessment and portfolio optimization"
          />
          <FeatureCard
            icon={<FaBrain className="text-4xl text-purple-500" />}
            title="AI Insights"
            description="Intelligent recommendations powered by advanced AI models"
          />
        </div>

        {/* Technology Stack */}
        <div className="mt-20 text-center">
          <h2 className="text-3xl font-bold mb-8">Powered By</h2>
          <div className="flex flex-wrap justify-center gap-6 text-gray-400">
            <TechBadge name="OpenAI GPT-4" />
            <TechBadge name="CrewAI" />
            <TechBadge name="LangChain" />
            <TechBadge name="Next.js" />
            <TechBadge name="FastAPI" />
            <TechBadge name="PostgreSQL" />
          </div>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="p-6 bg-dark-800 rounded-xl border border-dark-700 hover:border-primary-500 transition card-hover">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  );
}

function TechBadge({ name }) {
  return (
    <span className="px-4 py-2 bg-dark-800 rounded-full border border-dark-700">
      {name}
    </span>
  );
}