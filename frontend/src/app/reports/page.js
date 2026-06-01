'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isTokenValid } from '@/lib/auth';
import { reportAPI } from '@/lib/api';
import { formatDateTime } from '@/lib/utils';
import AppShell from '@/components/layout/AppShell';

import LoadingSpinner from '@/components/common/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  FaFileAlt,
  FaDownload,
  FaEye,
  FaRobot,
  FaSpinner,
  FaChartBar,
} from 'react-icons/fa';

export default function Reports() {
  const router = useRouter();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);

  useEffect(() => {
    if (!isTokenValid()) {
      router.push('/login');
      return;
    }
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const response = await reportAPI.getReports();
      setReports(response.data);
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzePortfolio = async () => {
    setAnalyzing(true);
    toast.loading('Running AI analysis... This may take a moment.', { duration: 5000 });

    try {
      const response = await reportAPI.analyzePortfolio();
      toast.success('Analysis completed!');
      fetchReports();
      setSelectedReport(response.data);
    } catch (error) {
      toast.error('Failed to analyze portfolio');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleViewReport = async (reportId) => {
    try {
      const response = await reportAPI.getReport(reportId);
      setSelectedReport(response.data);
    } catch (error) {
      toast.error('Failed to load report');
    }
  };

  const handleGeneratePDF = async (reportId) => {
    try {
      toast.loading('Generating PDF...');
      await reportAPI.generatePDF(reportId);
      toast.success('PDF generated!');
      
      // Download the PDF
      const downloadUrl = reportAPI.downloadReport(reportId);
      window.open(downloadUrl, '_blank');
    } catch (error) {
      toast.error('Failed to generate PDF');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner text="Loading reports..." />
      </div>
    );
  }

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">AI Reports</h1>
          <p className="text-gray-400">
            Generate comprehensive AI-powered financial reports
          </p>
        </div>
        <button
          onClick={handleAnalyzePortfolio}
          disabled={analyzing}
          className="flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-dark-600 rounded-lg font-semibold transition"
        >
          {analyzing ? (
            <>
              <FaSpinner className="animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <FaRobot />
              Run AI Analysis
            </>
          )}
        </button>
      </div>

      {/* Analysis Info Cards */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <InfoCard
          icon={<FaRobot className="text-3xl text-primary-500" />}
          title="Multi-Agent Analysis"
          description="5 specialized AI agents analyze your portfolio from different angles"
        />
        <InfoCard
          icon={<FaChartBar className="text-3xl text-green-500" />}
          title="Comprehensive Insights"
          description="Market research, sentiment analysis, risk assessment, and optimization"
        />
        <InfoCard
          icon={<FaFileAlt className="text-3xl text-yellow-500" />}
          title="Professional Reports"
          description="Institutional-grade reports with actionable recommendations"
        />
      </div>

      {/* Reports List */}
      <div className="bg-dark-800 border border-dark-700 rounded-xl overflow-hidden">
        <div className="p-6 border-b border-dark-700">
          <h2 className="text-xl font-bold">Your Reports</h2>
        </div>

        {reports.length === 0 ? (
          <div className="p-12 text-center">
            <FaFileAlt className="text-5xl text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 mb-4">No reports yet</p>
            <p className="text-sm text-gray-500">
              Click "Run AI Analysis" to generate your first report
            </p>
          </div>
        ) : (
          <div className="divide-y divide-dark-700">
            {reports.map((report) => (
              <div
                key={report.id}
                className="p-6 hover:bg-dark-700/50 transition cursor-pointer"
                onClick={() => handleViewReport(report.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold mb-1">{report.title}</h3>
                    <p className="text-sm text-gray-400 mb-2">{report.summary}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>{formatDateTime(report.created_at)}</span>
                      <span className="px-2 py-1 bg-primary-500/20 text-primary-400 rounded">
                        {report.report_type}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleViewReport(report.id);
                      }}
                      className="p-3 bg-dark-900 hover:bg-primary-600 rounded-lg transition"
                    >
                      <FaEye />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleGeneratePDF(report.id);
                      }}
                      className="p-3 bg-dark-900 hover:bg-green-600 rounded-lg transition"
                    >
                      <FaDownload />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Report View Modal */}
      {selectedReport && (
        <ReportModal report={selectedReport} onClose={() => setSelectedReport(null)} />
      )}
    </AppShell>
  );
}

function InfoCard({ icon, title, description }) {
  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl p-6">
      <div className="mb-3">{icon}</div>
      <h3 className="font-semibold mb-2">{title}</h3>
      <p className="text-sm text-gray-400">{description}</p>
    </div>
  );
}

function ReportModal({ report, onClose }) {
  const analysisData = report.content?.analysis || report.content;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-dark-800 border border-dark-700 rounded-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto my-8">
        <div className="sticky top-0 bg-dark-800 border-b border-dark-700 p-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold">{report.title}</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-dark-700 rounded-lg transition text-2xl"
          >
            ✕
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Executive Summary */}
          {report.summary && (
            <div>
              <h3 className="text-xl font-bold mb-3 text-primary-400">Executive Summary</h3>
              <p className="text-gray-300 leading-relaxed">{report.summary}</p>
            </div>
          )}

          {/* Market Analysis */}
          {analysisData?.market_analysis && (
            <div>
              <h3 className="text-xl font-bold mb-3 text-green-400">Market Research Analysis</h3>
              <div className="bg-dark-900 rounded-lg p-4 border border-dark-700">
                <p className="text-gray-300 whitespace-pre-wrap">
                  {typeof analysisData.market_analysis === 'string'
                    ? analysisData.market_analysis
                    : analysisData.market_analysis.analysis || JSON.stringify(analysisData.market_analysis, null, 2)}
                </p>
              </div>
            </div>
          )}

          {/* Sentiment Analysis */}
          {analysisData?.sentiment_analysis && (
            <div>
              <h3 className="text-xl font-bold mb-3 text-yellow-400">News Sentiment Analysis</h3>
              <div className="bg-dark-900 rounded-lg p-4 border border-dark-700">
                <div className="flex items-center gap-4 mb-3">
                  <span className="text-sm text-gray-400">Sentiment:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    analysisData.sentiment_analysis.sentiment === 'bullish' ? 'bg-green-500/20 text-green-400' :
                    analysisData.sentiment_analysis.sentiment === 'bearish' ? 'bg-red-500/20 text-red-400' :
                    'bg-gray-500/20 text-gray-400'
                  }`}>
                    {analysisData.sentiment_analysis.sentiment?.toUpperCase()}
                  </span>
                  <span className="text-sm text-gray-400">
                    Score: {(analysisData.sentiment_analysis.score * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-gray-300 whitespace-pre-wrap">
                  {analysisData.sentiment_analysis.analysis}
                </p>
              </div>
            </div>
          )}

          {/* Risk Analysis */}
          {analysisData?.risk_analysis && (
            <div>
              <h3 className="text-xl font-bold mb-3 text-red-400">Risk Assessment</h3>
              <div className="bg-dark-900 rounded-lg p-4 border border-dark-700">
                <div className="flex items-center gap-4 mb-3">
                  <span className="text-sm text-gray-400">Risk Level:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    analysisData.risk_analysis.risk_level === 'Low' ? 'bg-green-500/20 text-green-400' :
                    analysisData.risk_analysis.risk_level === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {analysisData.risk_analysis.risk_level}
                  </span>
                  <span className="text-sm text-gray-400">
                    Score: {analysisData.risk_analysis.risk_score}/100
                  </span>
                </div>
                <p className="text-gray-300 whitespace-pre-wrap">
                  {analysisData.risk_analysis.analysis}
                </p>
              </div>
            </div>
          )}

          {/* Optimization Recommendations */}
          {analysisData?.optimization && (
            <div>
              <h3 className="text-xl font-bold mb-3 text-purple-400">
                Portfolio Optimization
              </h3>
              <div className="bg-dark-900 rounded-lg p-4 border border-dark-700">
                <p className="text-gray-300 whitespace-pre-wrap mb-4">
                  {analysisData.optimization.analysis}
                </p>
                {analysisData.optimization.recommendations?.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">Key Recommendations:</h4>
                    <ul className="list-disc list-inside space-y-1 text-gray-300">
                      {analysisData.optimization.recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Full Report Content */}
          {report.content && typeof report.content === 'string' && (
            <div>
              <h3 className="text-xl font-bold mb-3">Full Report</h3>
              <div className="bg-dark-900 rounded-lg p-4 border border-dark-700">
                <p className="text-gray-300 whitespace-pre-wrap">{report.content}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}