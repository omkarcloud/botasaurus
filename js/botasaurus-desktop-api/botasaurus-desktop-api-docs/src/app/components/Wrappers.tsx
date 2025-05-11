export const Container = ({ children }) => {
  return (
    <div
      className="pt-6"
      style={{
        paddingLeft: '16px',
        paddingRight: '16px',
        paddingBottom: '32px',
        margin: '0 auto',
        maxWidth: '800px',
      }}>
      {children}
    </div>
  )
}