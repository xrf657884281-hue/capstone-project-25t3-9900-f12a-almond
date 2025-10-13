const style = {
  title: `text-4xl font-bold text-center mb-4`,
  subtitle: `text-lg text-center mb-6 font-base`,
  container: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-20 py-12',
  grid: 'grid md:grid-cols-2 gap-12 items-center',
  text_1: 'text-3xl font-semibold mb-4 text-center',
  main_text: 'text-lg mb-4 px-8',
  photo_detail: 'w-full h-auto rounded-lg shadow-lg',
}

const About = () => {
  return (
    <div>
      <p className={style.title}>Welcome to TruthLab</p>
      <p className = {style.subtitle}>
        Building a more trustworthy information world through the power of AI
      </p>
      <section className={style.container}>
        <div className={style.grid}>
          <div>
            <p className={style.text_1}>Our Mission</p>
            <div className={style.main_text}> TruthLab aims to empower researchers and educators to combat AI-generated 
            misinformation through systematic experimentation. Fake news detection 
            systems play a crucial role in maintaining information integrity and public 
            trust. To do so, you require a comprehensive research platform that can 
            efficiently generate synthetic fake news, test detection models, and advance 
            detection capabilities. 
            <br /><br />
            <span className="font-semibold text-gray-900 dark:text-gray-100">
            The problem is, the speed, scale, and sophistication of AI-generated
            misinformation can stretch research teams and their resources thin.</span></div>
          </div>
          <div className={style.photo_detail}>
            <img src="/public/About-us_1.jpg" alt="About_us_1" />
          </div>
        </div>
      </section>
      <section className={style.container}>
        <div className={style.grid}>
          <div>
            <img src="/public/About_story-2.jpg" alt="About_us_2" />
          </div>
          <div>
            <p className={style.text_1}>Our Story</p>
            <div className={style.main_text}>
              We're a research team from UNSW Computer Science & Engineering, 
              passionate about understanding how AI creates and detects fake news. 
              <br /><br />
              <span className="font-semibold text-gray-900 dark:text-gray-100">Think of us as the people asking: "If AI can lie, can it also catch
              itself lying?"</span>
              <br /> <br />
              We bring together expertise in machine learning, NLP, 
              and multimodal analysis to tackle one of the biggest challenges in 
              the AI era.
            </div>
          </div>
        </div>
      </section>
      <section className={style.container}>
  <h2 className="text-4xl font-bold text-center mb-24">Our Operating Principles</h2>
  
  <div className="grid md:grid-cols-2 gap-12 lg:gap-24">
    
    {/* Principle 1 */}
    <div className="px-6">
      <h3 className="text-2xl font-bold mb-4">Research Integrity First</h3>
      <p className="text-lg text-gray-700 dark:text-gray-300">
        When research advances, we all win. We build transparent and reproducible
        platforms that stay focused on solving the most pressing challenges in
        misinformation detection. This isn't just talk — it's our research model.
      </p>
    </div>

    {/* Principle 2 */}
    <div className="px-6">
      <h3 className="text-2xl font-bold mb-4">Drive Innovation</h3>
      <p className="text-lg text-gray-700 dark:text-gray-300">
        Use systematic experimentation to connect the dots between generation
        and detection. Take ownership of failure analysis, be accountable for
        improvements, and deliver actionable insights. Innovation speaks louder
        than assumptions.
      </p>
    </div>

    {/* Principle 3 */}
    <div className="px-6">
      <h3 className="text-2xl font-bold mb-4">Collaborate Openly</h3>
      <p className="text-lg text-gray-700 dark:text-gray-300">
        We succeed together or not at all. By sharing datasets, methods, and
        findings across the research community, we keep collaboration authentic
        and progress transparent. Ask questions, share expertise, and join forces
        to advance detection capabilities.
      </p>
    </div>

    {/* Principle 4 */}
    <div className="px-6">
      <h3 className="text-2xl font-bold mb-4">Stay Ahead</h3>
      <p className="text-lg text-gray-700 dark:text-gray-300">
        Just as AI evolves to generate more sophisticated misinformation, 
        improvement is central to who we are. Never stop learning from emerging 
        threats and detection strategies. Question current methods. This instinct 
        to push forward ensures that we're ahead of the curve.
      </p>
    </div>

  </div>
</section>
    </div>
  )
}

export default About