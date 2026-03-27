import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'https://compare-cart-263s.onrender.com'

function App() {
  const [keyword, setKeyword] = useState('')
  const [platform, setPlatform] = useState('amazon')
  const [numProducts, setNumProducts] = useState(10)
  const [products, setProducts] = useState([])
  const [selectedProducts, setSelectedProducts] = useState([])
  const [marketingPack, setMarketingPack] = useState(null)
  const [comparisons, setComparisons] = useState([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('products')

  const api = axios.create({ baseURL: API_BASE })

  useEffect(() => {
    loadProducts()
    loadComparisons()
  }, [])

  const loadProducts = async () => {
    try {
      const res = await api.get('/api/products')
      setProducts(res.data)
    } catch (err) {
      console.error('Error loading products:', err)
    }
  }

  const loadComparisons = async () => {
    try {
      const res = await api.get('/api/comparisons')
      setComparisons(res.data)
    } catch (err) {
      console.error('Error loading comparisons:', err)
    }
  }

  const handleScrape = async () => {
    if (!keyword) {
      alert('Please enter a search keyword')
      return
    }
    setLoading(true)
    try {
      const res = await api.post('/api/scrape', {
        keyword,
        platform,
        num_products: numProducts
      })
      await loadProducts()
      setSelectedProducts([])
      setActiveTab('products')
    } catch (err) {
      alert('Error: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  const toggleProductSelection = (product) => {
    const isSelected = selectedProducts.some(p => p.id === product.id)
    if (isSelected) {
      setSelectedProducts(selectedProducts.filter(p => p.id !== product.id))
    } else {
      setSelectedProducts([...selectedProducts, product])
    }
  }

  const handleCreateComparison = async () => {
    if (selectedProducts.length < 2) {
      alert('Please select at least 2 products to compare')
      return
    }
    setLoading(true)
    try {
      await api.post('/api/comparisons', {
        product_ids: selectedProducts.map(p => p.id),
        name: `Comparison ${new Date().toLocaleDateString()}`
      })
      await loadComparisons()
      setSelectedProducts([])
      setActiveTab('comparisons')
    } catch (err) {
      alert('Error: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteComparison = async (id) => {
    try {
      await api.delete(`/api/comparisons/${id}`)
      await loadComparisons()
    } catch (err) {
      alert('Error: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleGenerateMarketing = async () => {
    if (products.length === 0) {
      alert('Please scrape products first')
      return
    }
    setLoading(true)
    try {
      const res = await api.post('/api/generate-marketing', {
        products
      })
      setMarketingPack(res.data.marketing_pack)
      setActiveTab('marketing')
    } catch (err) {
      alert('Error: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  const handleClearProducts = async () => {
    try {
      await api.delete('/api/products')
      setProducts([])
      setSelectedProducts([])
      setMarketingPack(null)
    } catch (err) {
      alert('Error: ' + (err.response?.data?.detail || err.message))
    }
  }

  const exportComparison = (comparison) => {
    const data = {
      name: comparison.name,
      generated: new Date().toISOString(),
      analysis: comparison.analysis,
      products: comparison.products.map(p => ({
        name: p.name,
        price: p.price,
        rating: p.rating,
        reviews: p.sold,
        platform: p.platform,
        link: p.link
      }))
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `comparison-${comparison.name.replace(/\s+/g, '-').toLowerCase()}-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-blue-800 text-white p-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold">CompareCart</h1>
          <p className="text-blue-200">E-commerce Product Comparison & Intelligence</p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-4">
        <div className="flex gap-2 mb-4 border-b">
          {['products', 'comparisons', 'marketing'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 ${activeTab === tab ? 'border-b-2 border-blue-600 text-blue-600 font-semibold' : 'text-gray-600'}`}
            >
              {tab === 'products' && 'Products'}
              {tab === 'comparisons' && 'Comparisons'}
              {tab === 'marketing' && 'Marketing'}
            </button>
          ))}
        </div>

        {activeTab === 'products' && (
          <>
            <div className="bg-white rounded-lg p-4 mb-4">
              <h2 className="text-xl font-bold mb-4">Scrape Products</h2>
              <div className="flex gap-4 mb-4 flex-wrap">
                <input
                  type="text"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  placeholder="e.g., wireless earphones"
                  className="flex-1 min-w-48 p-2 border rounded"
                />
                <select
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value)}
                  className="p-2 border rounded"
                >
                  <option value="amazon">Amazon</option>
                  <option value="ebay">eBay</option>
                  <option value="walmart">Walmart</option>
                </select>
                <input
                  type="number"
                  value={numProducts}
                  onChange={(e) => setNumProducts(parseInt(e.target.value))}
                  min={1}
                  max={50}
                  className="p-2 border rounded w-24"
                />
                <button
                  onClick={handleScrape}
                  disabled={loading}
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Scraping...' : 'Scrape'}
                </button>
                <button
                  onClick={handleClearProducts}
                  className="border border-red-300 text-red-600 px-4 py-2 rounded hover:bg-red-50"
                >
                  Clear All
                </button>
              </div>
            </div>

            {selectedProducts.length >= 2 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                <div className="flex justify-between items-center">
                  <span className="text-yellow-800">{selectedProducts.length} products selected for comparison</span>
                  <button
                    onClick={handleCreateComparison}
                    className="bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700"
                  >
                    Create Comparison
                  </button>
                </div>
              </div>
            )}

            {products.length > 0 && (
              <div className="bg-white rounded-lg p-4 mb-4">
                <h2 className="text-xl font-bold mb-4">Found {products.length} Products</h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-gray-100">
                        <th className="p-2 text-left w-10">Select</th>
                        <th className="p-2 text-left">#</th>
                        <th className="p-2 text-left">Platform</th>
                        <th className="p-2 text-left">Product</th>
                        <th className="p-2 text-left">Price</th>
                        <th className="p-2 text-left">Rating</th>
                        <th className="p-2 text-left">Link</th>
                      </tr>
                    </thead>
                    <tbody>
                      {products.map((p, i) => (
                        <tr key={p.id} className={`border-b ${selectedProducts.some(s => s.id === p.id) ? 'bg-yellow-50' : ''}`}>
                          <td className="p-2">
                            <input
                              type="checkbox"
                              checked={selectedProducts.some(s => s.id === p.id)}
                              onChange={() => toggleProductSelection(p)}
                            />
                          </td>
                          <td className="p-2">{i + 1}</td>
                          <td className="p-2 capitalize">{p.platform}</td>
                          <td className="p-2 max-w-xs truncate">{p.name}</td>
                          <td className="p-2 font-semibold">{p.price}</td>
                          <td className="p-2">{p.rating}</td>
                          <td className="p-2">
                            {p.link ? (
                              <a href={p.link} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                View
                              </a>
                            ) : '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {products.length > 0 && (
              <div className="bg-white rounded-lg p-4">
                <h2 className="text-xl font-bold mb-4">Generate Marketing Pack</h2>
                <button
                  onClick={handleGenerateMarketing}
                  disabled={loading}
                  className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
                >
                  {loading ? 'Generating...' : 'Generate Marketing Pack'}
                </button>
              </div>
            )}
          </>
        )}

        {activeTab === 'comparisons' && (
          <div className="bg-white rounded-lg p-4">
            <h2 className="text-xl font-bold mb-4">Product Comparisons</h2>
            {comparisons.length === 0 ? (
              <p className="text-gray-500">No comparisons yet. Select products and create a comparison.</p>
            ) : (
              comparisons.map(comp => (
                <div key={comp.id} className="border rounded-lg p-4 mb-6">
                  <div className="flex justify-between items-center mb-4">
                    <div>
                      <h3 className="font-bold text-lg">{comp.name}</h3>
                      <p className="text-sm text-gray-500">{comp.products.length} products</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => exportComparison(comp)}
                        className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                      >
                        Export
                      </button>
                      <button
                        onClick={() => handleDeleteComparison(comp.id)}
                        className="text-red-600 hover:text-red-800 border border-red-300 px-3 py-1 rounded text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </div>

                  {comp.analysis && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                      <h4 className="font-semibold text-blue-800 mb-2">Analysis Summary</h4>
                      <div className="flex flex-wrap gap-4 text-sm">
                        {comp.analysis.lowest_price && (
                          <div className="bg-green-100 px-3 py-1 rounded">
                            <span className="text-green-800">💰 Best Price: </span>
                            <span className="font-bold">{comp.analysis.lowest_price.name.substring(0,30)}...</span>
                            <span className="text-green-700"> - ${comp.analysis.lowest_price.price.toFixed(2)}</span>
                          </div>
                        )}
                        {comp.analysis.highest_rating && (
                          <div className="bg-yellow-100 px-3 py-1 rounded">
                            <span className="text-yellow-800">⭐ Top Rated: </span>
                            <span className="font-bold">{comp.analysis.highest_rating.rating}★</span>
                            <span className="text-yellow-700"> - {comp.analysis.highest_rating.name.substring(0,25)}...</span>
                          </div>
                        )}
                        {comp.analysis.price_range && comp.analysis.price_range.min > 0 && (
                          <div className="bg-gray-100 px-3 py-1 rounded">
                            <span className="text-gray-800">📊 Price Range: </span>
                            <span className="font-bold">${comp.analysis.price_range.min.toFixed(2)} - ${comp.analysis.price_range.max.toFixed(2)}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="overflow-x-auto">
                    <table className="w-full text-sm border-collapse">
                      <thead>
                        <tr className="bg-gray-100">
                          <th className="p-2 text-left border">Attribute</th>
                          {comp.products.map((p, i) => (
                            <th key={i} className="p-2 text-left border min-w-[200px]">
                              <div className="font-semibold">{p.name.substring(0,40)}...</div>
                              <div className="text-xs text-gray-500">{p.platform}</div>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td className="p-2 border font-medium bg-gray-50">Image</td>
                          {comp.products.map((p, i) => (
                            <td key={i} className="p-2 border text-center">
                              {p.image ? (
                                <img src={p.image} alt={p.name} className="w-20 h-20 object-contain mx-auto" />
                              ) : (
                                <span className="text-gray-400">No Image</span>
                              )}
                            </td>
                          ))}
                        </tr>
                        <tr>
                          <td className="p-2 border font-medium bg-gray-50">Price</td>
                          {comp.products.map((p, i) => {
                            const isLowest = comp.analysis?.lowest_price?.id === p.id;
                            return (
                              <td key={i} className={`p-2 border text-center ${isLowest ? 'bg-green-50' : ''}`}>
                                <span className={`text-lg font-bold ${isLowest ? 'text-green-600' : 'text-blue-600'}`}>
                                  {p.price || 'N/A'}
                                </span>
                                {isLowest && <span className="block text-xs text-green-600">★ Best Price</span>}
                              </td>
                            );
                          })}
                        </tr>
                        <tr>
                          <td className="p-2 border font-medium bg-gray-50">Rating</td>
                          {comp.products.map((p, i) => {
                            const isHighest = comp.analysis?.highest_rating?.id === p.id;
                            return (
                              <td key={i} className={`p-2 border text-center ${isHighest ? 'bg-yellow-50' : ''}`}>
                                <span className={isHighest ? 'text-yellow-600 font-bold' : ''}>
                                  {p.rating || 'N/A'}
                                </span>
                                {isHighest && <span className="block text-xs text-yellow-600">★ Top Rated</span>}
                              </td>
                            );
                          })}
                        </tr>
                        <tr>
                          <td className="p-2 border font-medium bg-gray-50">Reviews</td>
                          {comp.products.map((p, i) => (
                            <td key={i} className="p-2 border text-center">{p.sold || 'N/A'}</td>
                          ))}
                        </tr>
                        {comp.products.some(p => p.original_price) && (
                          <tr>
                            <td className="p-2 border font-medium bg-gray-50">Original Price</td>
                            {comp.products.map((p, i) => (
                              <td key={i} className="p-2 border text-center text-gray-500">
                                {p.original_price || 'N/A'}
                              </td>
                            ))}
                          </tr>
                        )}
                        {comp.products.some(p => p.location) && (
                          <tr>
                            <td className="p-2 border font-medium bg-gray-50">Location</td>
                            {comp.products.map((p, i) => (
                              <td key={i} className="p-2 border text-center">{p.location || 'N/A'}</td>
                            ))}
                          </tr>
                        )}
                        <tr>
                          <td className="p-2 border font-medium bg-gray-50">Link</td>
                          {comp.products.map((p, i) => (
                            <td key={i} className="p-2 border text-center">
                              {p.link ? (
                                <a href={p.link} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-sm">
                                  View on {p.platform}
                                </a>
                              ) : (
                                <span className="text-gray-400 text-sm">No Link</span>
                              )}
                            </td>
                          ))}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'marketing' && (
          <>
            {marketingPack && (
              <div className="bg-white rounded-lg p-4">
                <h2 className="text-xl font-bold mb-4">Marketing Starter Pack</h2>
                
                <div className="flex gap-2 mb-4 border-b overflow-x-auto">
                  {['seo', 'ads', 'keywords', 'images'].map(tab => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab('marketing')}
                      className={`px-4 py-2 whitespace-nowrap ${tab === 'seo' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600'}`}
                    >
                      {tab === 'seo' && 'SEO Content'}
                      {tab === 'ads' && 'Ad Copy'}
                      {tab === 'keywords' && 'Keywords'}
                      {tab === 'images' && 'Image Prompts'}
                    </button>
                  ))}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {marketingPack.seo_titles && (
                    <div className="border rounded p-4">
                      <h3 className="font-bold text-lg mb-2">SEO Titles</h3>
                      <div className="bg-gray-100 p-2 rounded mb-2">{marketingPack.seo_titles.primary}</div>
                      {marketingPack.seo_titles.variations?.map((v, i) => (
                        <div key={i} className="text-sm text-gray-600 mb-1">{i + 1}. {v}</div>
                      ))}
                    </div>
                  )}

                  {marketingPack.description && (
                    <div className="border rounded p-4">
                      <h3 className="font-bold text-lg mb-2">Product Description</h3>
                      <p>{marketingPack.description}</p>
                    </div>
                  )}

                  {marketingPack.google_ads && (
                    <div className="border rounded p-4">
                      <h3 className="font-bold text-lg mb-2">Google Ads</h3>
                      {marketingPack.google_ads.map((ad, i) => (
                        <div key={i} className="bg-gray-100 p-2 rounded mb-2 text-sm">{ad}</div>
                      ))}
                    </div>
                  )}

                  {marketingPack.social_ads && (
                    <div className="border rounded p-4">
                      <h3 className="font-bold text-lg mb-2">Social Ads</h3>
                      {marketingPack.social_ads.facebook && (
                        <div className="mb-3">
                          <h4 className="font-semibold text-sm mb-1">Facebook:</h4>
                          {marketingPack.social_ads.facebook.map((ad, i) => (
                            <div key={i} className="bg-gray-100 p-2 rounded mb-1 text-sm">{ad}</div>
                          ))}
                        </div>
                      )}
                      {marketingPack.social_ads.instagram && (
                        <div>
                          <h4 className="font-semibold text-sm mb-1">Instagram:</h4>
                          {marketingPack.social_ads.instagram.map((ad, i) => (
                            <div key={i} className="bg-gray-100 p-2 rounded mb-1 text-sm">{ad}</div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {marketingPack.keywords && (
                    <div className="border rounded p-4">
                      <h3 className="font-bold text-lg mb-2">Keywords</h3>
                      {marketingPack.keywords.primary && (
                        <div className="mb-2">
                          <h4 className="font-semibold text-sm">Primary:</h4>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {marketingPack.keywords.primary.map((kw, i) => (
                              <span key={i} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">{kw}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {marketingPack.keywords.long_tail && (
                        <div>
                          <h4 className="font-semibold text-sm">Long-tail:</h4>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {marketingPack.keywords.long_tail.map((kw, i) => (
                              <span key={i} className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">{kw}</span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {marketingPack.image_prompts && (
                    <div className="border rounded p-4">
                      <h3 className="font-bold text-lg mb-2">Image Prompts</h3>
                      {marketingPack.image_prompts.midjourney?.map((prompt, i) => (
                        <details key={i} className="mb-2">
                          <summary className="cursor-pointer bg-gray-100 p-2 rounded text-sm">Midjourney #{i + 1}</summary>
                          <pre className="bg-gray-800 text-white p-2 mt-1 rounded text-xs overflow-x-auto">{prompt}</pre>
                        </details>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default App
