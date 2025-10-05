import React from 'react'
import Theme from '../components/Navigation/Navbar/Theme'

const Home = () => {
  return (
    <div>
      <Theme/>
      <h1 className="text-4xl font-bold">Welcome to the Home Page</h1>
      <p className="mt-4 text-lg">This is the home page of our application.</p>
    </div>
  )
}

export default Home
