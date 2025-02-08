import { useRouter } from 'next/router';
import Link from 'next/link';

export default function Home() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Dispute Resolution</h1>
          <p className="text-gray-600">Choose your destination</p>
        </div>
        
        <div className="space-y-4">
          <Link 
            href="/chat"
            className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10"
          >
            Chat Window
          </Link>
          
          <Link
            href="/admin"
            className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white border-blue-600 hover:bg-gray-50 md:py-4 md:text-lg md:px-10"
          >
            Admin Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}