import React, { useEffect, useRef } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import GUI from 'lil-gui'

import earthVertexShader from '@/components/Earth/shaders/earth/vertex.glsl?raw'
import earthFragmentShader from '@/components/Earth/shaders/earth/fragment.glsl?raw'
import atmosphereVertexShader from '@/components/Earth/shaders/atmosphere/vertex.glsl?raw'
import atmosphereFragmentShader from '@/components/Earth/shaders/atmosphere/fragment.glsl?raw'

type EarthCanvasProps = {
  className?: string
}

const EarthCanvas: React.FC<EarthCanvasProps> = ({ className }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const containerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    // ----- Renderer -----
    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: false,
      powerPreference: 'high-performance',
    })
    const sizes = {
      width: canvas.clientWidth || window.innerWidth,
      height: canvas.clientHeight || window.innerHeight,
      pixelRatio: Math.min(window.devicePixelRatio, 2),
    }
    renderer.setSize(sizes.width, sizes.height, false)
    renderer.setPixelRatio(sizes.pixelRatio)
    renderer.setClearColor(0x000000, 0)

    // ----- Scene & Camera -----
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(25, sizes.width / sizes.height, 0.1, 100)
    camera.position.set(12, 5, 4)
    scene.add(camera)

    // ----- Controls -----
    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true

    // ----- GUI -----
    const gui = new GUI({ 
      container: containerRef.current || document.body,
      width: 320,
      title: 'Controls'
    })
    
    // Change Guide frmework location
    const guiElement = gui.domElement as HTMLElement
    guiElement.style.position = 'absolute'
    guiElement.style.top = '0'
    guiElement.style.right = '0'
    guiElement.style.zIndex = '10'
    
    const earthParameters = {
      atmosphereDayColor: '#00aaff',
      atmosphereTwilightColor: '#ff6600',
    }

    // ----- Loaders -----
    const textureLoader = new THREE.TextureLoader()
    const earthDayTexture = textureLoader.load('./public/earth/day.jpg')
    earthDayTexture.colorSpace = THREE.SRGBColorSpace
    earthDayTexture.anisotropy = 8

    const earthNightTexture = textureLoader.load('/public/earth/night.jpg')
    earthNightTexture.colorSpace = THREE.SRGBColorSpace
    earthNightTexture.anisotropy = 8

    const earthSpecularCloudsTexture = textureLoader.load('/public/earth/specularClouds.jpg')
    earthSpecularCloudsTexture.anisotropy = 8

    // ----- Earth Mesh -----
    const earthGeometry = new THREE.SphereGeometry(2, 64, 64)
    const earthMaterial = new THREE.ShaderMaterial({
      vertexShader: earthVertexShader,
      fragmentShader: earthFragmentShader,
      uniforms: {
        uDayTexture: new THREE.Uniform(earthDayTexture),
        uNightTexture: new THREE.Uniform(earthNightTexture),
        uSpecularCloudsTexture: new THREE.Uniform(earthSpecularCloudsTexture),
        uSunDirection: new THREE.Uniform(new THREE.Vector3(0, 0, 1)),
        uAtmosphereDayColor: new THREE.Uniform(new THREE.Color(earthParameters.atmosphereDayColor)),
        uAtmosphereTwilightColor: new THREE.Uniform(
          new THREE.Color(earthParameters.atmosphereTwilightColor),
        ),
      },
      transparent: false,
    })
    const earth = new THREE.Mesh(earthGeometry, earthMaterial)
    scene.add(earth)

    // ----- Atmosphere -----
    const atmosphereMaterial = new THREE.ShaderMaterial({
      side: THREE.BackSide,
      transparent: true,
      vertexShader: atmosphereVertexShader,
      fragmentShader: atmosphereFragmentShader,
      uniforms: {
        uSunDirection: new THREE.Uniform(new THREE.Vector3(0, 0, 1)),
        uAtmosphereDayColor: new THREE.Uniform(new THREE.Color(earthParameters.atmosphereDayColor)),
        uAtmosphereTwilightColor: new THREE.Uniform(
          new THREE.Color(earthParameters.atmosphereTwilightColor),
        ),
      },
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    })
    const atmosphere = new THREE.Mesh(earthGeometry.clone(), atmosphereMaterial)
    atmosphere.scale.set(1.04, 1.04, 1.04)
    scene.add(atmosphere)

    // ----- Sun -----
    const sunSpherical = new THREE.Spherical(1, Math.PI * 0.5, 0.5)
    const sunDirection = new THREE.Vector3()

    const debugSun = new THREE.Mesh(
      new THREE.IcosahedronGeometry(0.1, 2),
      new THREE.MeshBasicMaterial({ color: 0xff8c00 }),
    )
    scene.add(debugSun)

    const updateSun = () => {
      sunDirection.setFromSpherical(sunSpherical)
      debugSun.position.copy(sunDirection).multiplyScalar(5)
      ;(earthMaterial.uniforms.uSunDirection.value as THREE.Vector3).copy(sunDirection)
      ;(atmosphereMaterial.uniforms.uSunDirection.value as THREE.Vector3).copy(sunDirection)
    }
    updateSun()

    gui
      .add(sunSpherical, 'phi', 0, Math.PI, 0.001)
      .name('Sun φ')
      .onChange(updateSun)
    gui
      .add(sunSpherical, 'theta', -Math.PI, Math.PI, 0.001)
      .name('Sun θ')
      .onChange(updateSun)

    gui
      .addColor(earthParameters, 'atmosphereDayColor')
      .name('Day Color')
      .onChange(() => {
        ;(earthMaterial.uniforms.uAtmosphereDayColor.value as THREE.Color).set(
          earthParameters.atmosphereDayColor,
        )
        ;(atmosphereMaterial.uniforms.uAtmosphereDayColor.value as THREE.Color).set(
          earthParameters.atmosphereDayColor,
        )
      })

    gui
      .addColor(earthParameters, 'atmosphereTwilightColor')
      .name('Twilight Color')
      .onChange(() => {
        ;(earthMaterial.uniforms.uAtmosphereTwilightColor.value as THREE.Color).set(
          earthParameters.atmosphereTwilightColor,
        )
        ;(atmosphereMaterial.uniforms.uAtmosphereTwilightColor.value as THREE.Color).set(
          earthParameters.atmosphereTwilightColor,
        )
      })

    // ----- Resize -----
    const onResize = () => {
      const width = canvas.clientWidth || window.innerWidth
      const height = canvas.clientHeight || window.innerHeight
      sizes.width = width
      sizes.height = height
      sizes.pixelRatio = Math.min(window.devicePixelRatio, 2)

      camera.aspect = sizes.width / sizes.height
      camera.updateProjectionMatrix()

      renderer.setSize(sizes.width, sizes.height, false)
      renderer.setPixelRatio(sizes.pixelRatio)
    }
    window.addEventListener('resize', onResize)

    // ----- Animate -----
    let raf = 0
    const clock = new THREE.Clock()

    const tick = () => {
      const elapsedTime = clock.getElapsedTime()

      earth.rotation.y = elapsedTime * 0.1

      controls.update()
      renderer.render(scene, camera)
      raf = window.requestAnimationFrame(tick)
    }
    tick()

    // ----- Cleanup -----
    return () => {
      window.cancelAnimationFrame(raf)
      window.removeEventListener('resize', onResize)
      gui.destroy()
      controls.dispose()

      earthGeometry.dispose()
      earthMaterial.dispose()
      atmosphereMaterial.dispose()

      earthDayTexture.dispose()
      earthNightTexture.dispose()
      earthSpecularCloudsTexture.dispose()

      renderer.dispose()
      scene.clear()
    }
  }, [])

  return (
    <div 
      ref={containerRef}
      style={{ 
        width: '100%', 
        height: '100%', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      <canvas
        ref={canvasRef}
        className={className ?? 'webgl'}
        style={{ 
          width: '100%', 
          height: '100%', 
          display: 'block'
        }}
      />
    </div>
  )
}

export default EarthCanvas