import React, { useState } from 'react';

const About = () => {
  const [count, setCount] = useState(0);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#000510] text-white p-8">
      <h1 className="text-4xl font-bold mb-4">About Page</h1>
      <p className="text-gray-400 mb-8">이곳은 간단한 테스트를 위한 소개 페이지입니다.</p>
      
      <div className="bg-white/5 p-10 rounded-3xl border border-white/10 backdrop-blur-lg shadow-2xl text-center">
        <h2 className="text-xl mb-6 text-blue-400 font-mono italic underline">Interactive Counter</h2>
        <button
          className="px-8 py-4 text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl hover:scale-105 transition-transform active:scale-95 shadow-[0_0_20px_rgba(37,99,235,0.4)]"
          onClick={() => setCount((prev) => prev + 1)}
        >
          Count is {count}
        </button>
        <p className="mt-4 text-gray-500 text-sm italic">Click to increase the number</p>
      </div>
    </div>
  );
};

export default About;